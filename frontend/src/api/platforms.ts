import apiClient from './client'
import type { PlatformAccount } from '../types/platform'

export const platformsApi = {
  list: () => apiClient.get<PlatformAccount[]>('/platforms'),

  getOAuthUrl: (platform: string) =>
    apiClient.get<{ oauth_url: string }>(`/platforms/${platform}/oauth-url`),

  disconnect: (accountId: string) =>
    apiClient.delete(`/platforms/${accountId}`),

  publish: (data: {
    video_variant_id: string
    platform_account_ids: string[]
    scheduled_at?: string
  }) => apiClient.post('/publish', data),
}
