import apiClient from './client'
import type {
  PlatformAccount,
  PublishJob,
  PublishRequest,
  MultiVariantPublishRequest,
  PromptHistoryEntry,
} from '../types/platform'

export const platformsApi = {
  list: () => apiClient.get<PlatformAccount[]>('/platforms'),

  getOAuthUrl: (platform: string) =>
    apiClient.get<{ oauth_url: string }>(`/platforms/${platform}/oauth-url`),

  disconnect: (accountId: string) =>
    apiClient.delete(`/platforms/${accountId}`),

  publish: (data: PublishRequest) =>
    apiClient.post<PublishJob[]>('/publish', data),

  publishMulti: (data: MultiVariantPublishRequest) =>
    apiClient.post<PublishJob[]>('/publish/multi', data),

  listJobs: (params?: { page?: number; platform?: string; status?: string }) =>
    apiClient.get<PublishJob[]>('/publish/jobs', { params }),

  getJob: (jobId: string) =>
    apiClient.get<PublishJob>(`/publish/jobs/${jobId}`),

  retryJob: (jobId: string) =>
    apiClient.post<PublishJob>(`/publish/jobs/${jobId}/retry`),

  cancelJob: (jobId: string) =>
    apiClient.delete(`/publish/jobs/${jobId}`),
}

export const promptsApi = {
  history: (page = 1) =>
    apiClient.get<PromptHistoryEntry[]>('/prompts/history', { params: { page } }),

  favorites: () =>
    apiClient.get<PromptHistoryEntry[]>('/prompts/favorites'),

  toggleFavorite: (promptId: string) =>
    apiClient.post<PromptHistoryEntry>(`/prompts/${promptId}/favorite`),

  delete: (promptId: string) =>
    apiClient.delete(`/prompts/${promptId}`),
}
