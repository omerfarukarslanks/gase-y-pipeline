import apiClient from './client'
import type { Video, VideoVariant, VideoGenerateRequest } from '../types/video'

export const videosApi = {
  generate: (data: VideoGenerateRequest) =>
    apiClient.post<Video>('/videos', data),

  get: (id: string) => apiClient.get<Video>(`/videos/${id}`),

  getVariants: (videoId: string) =>
    apiClient.get<VideoVariant[]>(`/videos/${videoId}/variants`),
}
