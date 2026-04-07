import { apiClient, type ApiResponse } from './client';

export interface AccountSummary {
  id: string;
  fullname: string;
  email: string;
  nickname: string;
  occupation: string;
  more_about_you: string;
  custom_instructions: string;
  plan_name: string;
  plan_renewal_date?: string | null;
  credits: number;
  free_credits: number;
  monthly_credits: number;
  monthly_credits_max: number;
  daily_refresh_credits: number;
  preferred_language: string;
  appearance: string;
  receive_product_updates: boolean;
  email_when_queued_task_starts: boolean;
}

export interface UsageItem {
  id: string;
  source_type: string;
  label: string;
  credits_delta: number;
  created_at: string;
}

export interface BillingItem {
  id: string;
  label: string;
  amount: number;
  currency: string;
  created_at: string;
}

export async function getAccountSummary(): Promise<AccountSummary> {
  const response = await apiClient.get<ApiResponse<AccountSummary>>('/account/summary');
  return response.data.data;
}

export async function updateAccountProfile(payload: Partial<AccountSummary>): Promise<AccountSummary> {
  const response = await apiClient.patch<ApiResponse<AccountSummary>>('/account/profile', payload);
  return response.data.data;
}

export async function updateAccountSettings(payload: Partial<AccountSummary>): Promise<AccountSummary> {
  const response = await apiClient.patch<ApiResponse<AccountSummary>>('/account/settings', payload);
  return response.data.data;
}

export async function getUsageItems(): Promise<UsageItem[]> {
  const response = await apiClient.get<ApiResponse<UsageItem[]>>('/account/usage');
  return response.data.data;
}

export async function getBillingItems(): Promise<BillingItem[]> {
  const response = await apiClient.get<ApiResponse<BillingItem[]>>('/account/billing');
  return response.data.data;
}
