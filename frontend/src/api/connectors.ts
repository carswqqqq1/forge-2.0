import { apiClient, type ApiResponse } from './client';

export interface ConnectorItem {
  connector_id: string;
  name: string;
  description: string;
  type: string;
  status: string;
  connected_at?: string | null;
  metadata: Record<string, any>;
}

export async function listConnectors(): Promise<ConnectorItem[]> {
  const response = await apiClient.get<ApiResponse<ConnectorItem[]>>('/connectors');
  return response.data.data;
}

export async function connectConnector(connectorId: string, payload: { auth_token?: string; metadata?: Record<string, any>; type?: string } = {}): Promise<ConnectorItem> {
  const response = await apiClient.post<ApiResponse<ConnectorItem>>(`/connectors/${connectorId}/connect`, payload);
  return response.data.data;
}

export async function disconnectConnector(connectorId: string): Promise<void> {
  await apiClient.delete<ApiResponse<Record<string, never>>>(`/connectors/${connectorId}`);
}
