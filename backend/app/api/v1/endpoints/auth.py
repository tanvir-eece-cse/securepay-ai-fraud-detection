"""
Authentication Endpoints
Handles user registration, login, MFA, and token management.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import secrets
import structlog

from app.core.database import get_db
from app.core.security import (
    PasswordService, JWTService, MFAService,
    get_current_user, encryption_service
)
from app.core.logging import audit_logger
from app.core.redis import session_store
from app.models.user import User, UserStatus
from app.schemas.user import (
    UserRegister, UserLogin, TokenResponse,
    RefreshTokenRequest, MFASetupResponse, MFAVerifyRequest
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (min 12 chars, uppercase, lowercase, digit, special char)
    - **first_name**: User's first name
    - **last_name**: User's last name
    - **phone**: Bangladesh phone number (optional)
    """
    
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        audit_logger.log_authentication(
            user_id=user_data.email,
            success=False,
            method="registration",
            ip_address=request.client.host if request.client else "unknown",
            reason="Email already registered"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check phone number if provided
    if user_data.phone:
        result = await db.execute(
            select(User).where(User.phone == user_data.phone)
        )
        existing_phone = result.scalar_one_or_none()
        
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
    
    # Hash password
    hashed_password = PasswordService.hash_password(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        organization=user_data.organization,
        department=user_data.department,
        job_title=user_data.job_title,
        status=UserStatus.ACTIVE,  # Auto-activate for demo; use PENDING in production
        password_changed_at=datetime.utcnow()
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Create tokens
    access_token = JWTService.create_access_token(
        data={"sub": str(new_user.id), "email": new_user.email, "role": new_user.role.value}
    )
    refresh_token = JWTService.create_refresh_token(
        data={"sub": str(new_user.id)}
    )
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    await session_store.create(
        session_id,
        {
            "user_id": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role.value,
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    # Update user session
    new_user.current_session_id = session_id
    new_user.last_login = datetime.utcnow()
    await db.commit()
    
    # Audit log
    audit_logger.log_authentication(
        user_id=str(new_user.id),
        success=True,
        method="registration",
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent")
    )
    
    logger.info(
        "User registered",
        user_id=str(new_user.id),
        email=new_user.email
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWTService.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        mfa_required=False
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    Returns access and refresh tokens.
    """
    
    # Find user
    result = await db.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        audit_logger.log_authentication(
            user_id=credentials.email,
            success=False,
            method="login",
            ip_address=request.client.host if request.client else "unknown",
            reason="User not found"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if account is locked
    if user.is_locked:
        audit_logger.log_authentication(
            user_id=str(user.id),
            success=False,
            method="login",
            ip_address=request.client.host if request.client else "unknown",
            reason="Account locked"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until}"
        )
    
    # Verify password
    if not PasswordService.verify_password(credentials.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        user.last_failed_login = datetime.utcnow()
        
        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            logger.warning(
                "Account locked due to failed login attempts",
                user_id=str(user.id),
                email=user.email
            )
        
        await db.commit()
        
        audit_logger.log_authentication(
            user_id=str(user.id),
            success=False,
            method="login",
            ip_address=request.client.host if request.client else "unknown",
            reason="Invalid password"
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Check if user is active
    if user.status != UserStatus.ACTIVE:
        audit_logger.log_authentication(
            user_id=str(user.id),
            success=False,
            method="login",
            ip_address=request.client.host if request.client else "unknown",
            reason=f"User status: {user.status.value}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active"
        )
    
    # Check MFA
    if user.mfa_enabled:
        if not credentials.mfa_code:
            return TokenResponse(
                access_token="",
                refresh_token="",
                expires_in=0,
                mfa_required=True
            )
        
        # Verify MFA code
        if not MFAService.verify_totp(user.mfa_secret, credentials.mfa_code):
            audit_logger.log_authentication(
                user_id=str(user.id),
                success=False,
                method="login_mfa",
                ip_address=request.client.host if request.client else "unknown",
                reason="Invalid MFA code"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Reset failed attempts
    user.failed_login_attempts = 0
    user.last_failed_login = None
    user.locked_until = None
    
    # Create tokens
    access_token = JWTService.create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "roles": [user.role.value]
        }
    )
    refresh_token = JWTService.create_refresh_token(
        data={"sub": str(user.id)}
    )
    
    # Create session
    session_id = secrets.token_urlsafe(32)
    await session_store.create(
        session_id,
        {
            "user_id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "created_at": datetime.utcnow().isoformat()
        }
    )
    
    # Update user
    user.current_session_id = session_id
    user.last_login = datetime.utcnow()
    user.last_activity = datetime.utcnow()
    await db.commit()
    
    # Audit log
    audit_logger.log_authentication(
        user_id=str(user.id),
        success=True,
        method="login",
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent")
    )
    
    logger.info(
        "User logged in",
        user_id=str(user.id),
        email=user.email
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes
        mfa_required=False
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    
    # Decode refresh token
    try:
        payload = JWTService.decode_token(token_request.refresh_token)
        
        if not JWTService.verify_token_type(payload, "refresh"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        
        # Get user
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = JWTService.create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "roles": [user.role.value]
            }
        )
        
        logger.info("Token refreshed", user_id=str(user.id))
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=token_request.refresh_token,
            expires_in=30 * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout current user and invalidate session.
    """
    
    user_id = current_user.get("sub")
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user and user.current_session_id:
        # Delete session
        await session_store.delete(user.current_session_id)
        
        # Clear session from user
        user.current_session_id = None
        await db.commit()
    
    audit_logger.log_authentication(
        user_id=user_id,
        success=True,
        method="logout",
        ip_address="unknown"
    )
    
    logger.info("User logged out", user_id=user_id)
    
    return {"message": "Successfully logged out"}


@router.post("/mfa/enable", response_model=MFASetupResponse)
async def enable_mfa(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Enable Multi-Factor Authentication for the current user.
    Returns QR code URI and backup codes.
    """
    
    user_id = current_user.get("sub")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled"
        )
    
    # Generate MFA secret and backup codes
    secret = MFAService.generate_secret()
    qr_uri = MFAService.get_totp_uri(secret, user.email)
    backup_codes = MFAService.generate_backup_codes()
    
    # Store encrypted backup codes
    encrypted_codes = [
        encryption_service.encrypt(code) for code in backup_codes
    ]
    
    # Save to user (but don't enable yet - requires verification)
    user.mfa_secret = secret
    user.backup_codes = encrypted_codes
    await db.commit()
    
    logger.info("MFA setup initiated", user_id=str(user.id))
    
    return MFASetupResponse(
        secret=secret,
        qr_uri=qr_uri,
        backup_codes=backup_codes
    )


@router.post("/mfa/verify")
async def verify_mfa(
    mfa_verify: MFAVerifyRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify and activate MFA using TOTP code.
    """
    
    user_id = current_user.get("sub")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.mfa_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA not set up"
        )
    
    # Verify code
    if not MFAService.verify_totp(user.mfa_secret, mfa_verify.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    # Enable MFA
    user.mfa_enabled = True
    await db.commit()
    
    audit_logger.log_security_event(
        event_name="mfa_enabled",
        severity="info",
        user_id=str(user.id)
    )
    
    logger.info("MFA enabled", user_id=str(user.id))
    
    return {"message": "MFA successfully enabled"}


@router.post("/mfa/disable")
async def disable_mfa(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Disable Multi-Factor Authentication.
    """
    
    user_id = current_user.get("sub")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # Disable MFA
    user.mfa_enabled = False
    user.mfa_secret = None
    user.backup_codes = None
    await db.commit()
    
    audit_logger.log_security_event(
        event_name="mfa_disabled",
        severity="warning",
        user_id=str(user.id)
    )
    
    logger.info("MFA disabled", user_id=str(user.id))
    
    return {"message": "MFA successfully disabled"}
