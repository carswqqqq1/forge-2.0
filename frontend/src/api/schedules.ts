import { apiClient, type ApiResponse } from './client';

export interface ForgeSchedule {
  schedule_id: string;
  name: string;
  description: string;
  schedule_text: string;
  cron_expression: string;
  next_run?: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export async function listSchedules(): Promise<ForgeSchedule[]> {
  const response = await apiClient.get<ApiResponse<ForgeSchedule[]>>('/schedules');
  return response.data.data;
}

export async function createSchedule(payload: Partial<ForgeSchedule>): Promise<ForgeSchedule> {
  const response = await apiClient.post<ApiResponse<ForgeSchedule>>('/schedules', payload);
  return response.data.data;
}

export async function updateSchedule(scheduleId: string, payload: Partial<ForgeSchedule>): Promise<ForgeSchedule> {
  const response = await apiClient.patch<ApiResponse<ForgeSchedule>>(`/schedules/${scheduleId}`, payload);
  return response.data.data;
}

export async function deleteSchedule(scheduleId: string): Promise<void> {
  await apiClient.delete<ApiResponse<Record<string, never>>>(`/schedules/${scheduleId}`);
}
