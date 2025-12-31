/**
 * Type definitions for SecurePay AI Frontend
 */

// User types
export interface User {
  id: string;
  email: string;
  full_name: string;
  phone_number?: string;
  role: UserRole;
  status: UserStatus;
  mfa_enabled: boolean;
  created_at: string;
  last_login?: string;
}

export type UserRole = 'admin' | 'analyst' | 'viewer';
export type UserStatus = 'active' | 'inactive' | 'locked';

// Authentication types
export interface LoginRequest {
  email: string;
  password: string;
  mfa_code?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  requires_mfa: boolean;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  phone_number?: string;
}

// Transaction types
export interface Transaction {
  id: string;
  transaction_id: string;
  amount: number;
  currency: string;
  sender_account: string;
  receiver_account: string;
  transaction_type: TransactionType;
  channel: TransactionChannel;
  status: TransactionStatus;
  fraud_score: number;
  risk_level: RiskLevel;
  is_fraudulent: boolean;
  explanation: string[];
  created_at: string;
  analyzed_at?: string;
}

export type TransactionType = 'transfer' | 'payment' | 'withdrawal' | 'deposit';
export type TransactionChannel = 'mobile_app' | 'web' | 'ussd' | 'api';
export type TransactionStatus = 'pending' | 'approved' | 'rejected' | 'flagged';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

export interface TransactionAnalyzeRequest {
  transaction_id: string;
  amount: number;
  currency: string;
  sender_account: string;
  receiver_account: string;
  transaction_type: TransactionType;
  channel: TransactionChannel;
  device_id?: string;
  ip_address?: string;
  location?: Location;
  metadata?: Record<string, unknown>;
}

export interface TransactionAnalyzeResponse extends Transaction {
  processing_time_ms: number;
  model_version: string;
}

// Alert types
export interface Alert {
  id: string;
  transaction_id: string;
  risk_level: RiskLevel;
  message: string;
  status: AlertStatus;
  created_at: string;
  reviewed_at?: string;
  reviewed_by?: string;
}

export type AlertStatus = 'pending' | 'acknowledged' | 'resolved' | 'dismissed';

// Analytics types
export interface DashboardStats {
  total_transactions: number;
  flagged_transactions: number;
  fraud_rate: number;
  total_amount_analyzed: number;
  alerts_pending: number;
  period: string;
}

export interface TrendData {
  timestamps: string[];
  transactions: number[];
  fraud_rates: number[];
  amounts: number[];
}

export interface RiskDistribution {
  low: number;
  medium: number;
  high: number;
  critical: number;
}

// Location types
export interface Location {
  lat: number;
  lon: number;
  city?: string;
  country?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  status_code: number;
  error_code?: string;
}

// Filter types
export interface TransactionFilters {
  risk_level?: RiskLevel;
  status?: TransactionStatus;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
}

// Chart types
export interface ChartDataPoint {
  name: string;
  value: number;
  fill?: string;
}

export interface TimeSeriesDataPoint {
  timestamp: string;
  value: number;
  label?: string;
}
