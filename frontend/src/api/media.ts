import apiClient from './client'
import type { MusicTrack } from '../types/video'

export const mediaApi = {
  // Music
  listTracks: (params?: { category?: string; mood?: string }) =>
    apiClient.get<MusicTrack[]>('/music/tracks', { params }),

  getTrack: (trackId: string) =>
    apiClient.get<MusicTrack>(`/music/tracks/${trackId}`),

  getCategories: () =>
    apiClient.get<{ categories: string[]; moods: string[] }>('/music/categories'),

  // Thumbnails
  generateThumbnail: (videoId: string, params?: { image_provider?: string; style?: string }) =>
    apiClient.post(`/videos/${videoId}/thumbnail`, null, { params }),

  // Subtitles
  generateSubtitles: (videoId: string, language: string) =>
    apiClient.post(`/videos/${videoId}/subtitles/${language}`),

  getSubtitleUrl: (videoId: string, language: string, format: 'srt' | 'vtt' = 'srt') =>
    `/api/v1/videos/${videoId}/subtitles/${language}?format=${format}`,
}
