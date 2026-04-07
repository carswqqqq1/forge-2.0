import { apiClient, type ApiResponse } from './client';

export interface ReferralInfo {
  invite_link: string;
  referral_code: string;
  credits_earned: number;
  referral_count: number;
}

export async function getReferralInfo(): Promise<ReferralInfo> {
  const response = await apiClient.get<ApiResponse<ReferralInfo>>('/referrals/my-link');
  return response.data.data;
}

export async function redeemReferral(code: string): Promise<ReferralInfo> {
  const response = await apiClient.post<ApiResponse<ReferralInfo>>('/referrals/redeem', { code });
  return response.data.data;
}
