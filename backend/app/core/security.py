"""
Security Module - The Heart of SecurePay's Security

Author: Md. Tanvir Hossain
Email: tanvir.eece.cse@gmail.com

Comprehensive security utilities including authentication, encryption, and security headers.

I spent a lot of time on this module because security is the #1 priority for a
financial platform. Key decisions:
- Argon2 over bcrypt: memory-hard, resistant to GPU attacks
- Fernet for field encryption: symmetric, provides authenticity
- TOTP for MFA: works with standard authenticator apps

The SecurityHeadersMiddleware adds OWASP-recommended headers automatically.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from argon2 import PasswordHasher
from cryptography.fernet import Fernet
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import pyotp
import hashlib
import secrets
import structlog
import base64

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
argon2_hasher = PasswordHasher()

# Security bearer scheme
security = HTTPBearer()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server header (use del instead of pop for MutableHeaders)
        if "Server" in response.headers:
            del response.headers["Server"]
        
        return response


class PasswordService:
    """Service for secure password handling."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using Argon2."""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def check_password_strength(password: str) -> Dict[str, Any]:
        """
        Check password strength and return analysis.
        Returns dict with 'valid' bool and 'issues' list.
        """
        issues = []
        
        if len(password) < 12:
            issues.append("Password must be at least 12 characters long")
        if not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            issues.append("Password must contain at least one special character")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "strength": "strong" if len(issues) == 0 else "weak" if len(issues) > 2 else "moderate"
        }


class JWTService:
    """Service for JWT token generation and validation."""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": secrets.token_urlsafe(32)  # Unique token ID
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.warning("JWT decode error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    def verify_token_type(payload: Dict[str, Any], expected_type: str) -> bool:
        """Verify the token type matches expected type."""
        return payload.get("type") == expected_type


class MFAService:
    """Service for Multi-Factor Authentication using TOTP."""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret."""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, email: str) -> str:
        """Generate TOTP URI for QR code generation."""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=settings.MFA_ISSUER
        )
    
    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        """Verify a TOTP code."""
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=settings.MFA_VALID_WINDOW)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """Generate backup codes for MFA recovery."""
        return [secrets.token_hex(4).upper() for _ in range(count)]


class EncryptionService:
    """Service for data encryption and decryption."""
    
    def __init__(self):
        # Derive a valid Fernet key from the encryption key
        key = hashlib.sha256(settings.ENCRYPTION_KEY.encode()).digest()
        self.fernet = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self.fernet.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt an encrypted string."""
        return self.fernet.decrypt(encrypted_data.encode()).decode()
    
    @staticmethod
    def hash_data(data: str) -> str:
        """Create a SHA-256 hash of data."""
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def mask_account_number(account: str) -> str:
        """Mask account number for display (show last 4 digits)."""
        if len(account) <= 4:
            return "*" * len(account)
        return "*" * (len(account) - 4) + account[-4:]
    
    @staticmethod
    def mask_phone_number(phone: str) -> str:
        """Mask phone number for display."""
        if len(phone) <= 4:
            return "*" * len(phone)
        return phone[:3] + "*" * (len(phone) - 6) + phone[-3:]


# Dependency for getting current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Dependency to extract and validate the current user from JWT token.
    """
    token = credentials.credentials
    payload = JWTService.decode_token(token)
    
    if not JWTService.verify_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return payload


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dependency to get current active (non-disabled) user.
    """
    if current_user.get("disabled"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


def require_roles(*roles: str):
    """
    Dependency factory for role-based access control.
    Usage: @router.get("/admin", dependencies=[Depends(require_roles("admin"))])
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


# Initialize encryption service
encryption_service = EncryptionService()
