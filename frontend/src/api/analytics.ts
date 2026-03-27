import apiClient from './client'

export interface AnalyticsOverview {
  total_videos: number
  total_published: number
  total_views: number
  total_likes: number
  total_comments: number
  total_shares: number
  platforms: Record<string, { published: number; views: number; likes: number }>
}

export interface TopPerforming {
  job_id: string
  platform: string
  platform_url: string | null
  published_at: string | null
  title: string | null
  language: string
  views: number
  likes: number
}

export interface CalendarEvent {
  id: string
  title: string
  language: string
  platform: string
  status: string
  date: string | null
  scheduled_at: string | null
  published_at: string | null
  platform_url: string | null
}

export const analyticsApi = {
  overview: () =>
    apiClient.get<AnalyticsOverview>('/analytics/overview'),

  topPerforming: (limit = 5) =>
    apiClient.get<TopPerforming[]>('/analytics/top-performing', { params: { limit } }),

  jobSnapshots: (jobId: string) =>
    apiClient.get<Array<{
      views: number; likes: number; comments: number; shares: number;
      watch_time_sec: number | null; snapshot_at: string
    }>>(`/analytics/jobs/${jobId}/snapshots`),
}

export const calendarApi = {
  events: (params?: { start?: string; end?: string; platform?: string }) =>
    apiClient.get<{ events: CalendarEvent[] }>('/schedule/calendar', { params }),

  reschedule: (jobId: string, scheduledAt: string) =>
    apiClient.put(`/schedule/jobs/${jobId}/reschedule`, null, {
      params: { scheduled_at: scheduledAt },
    }),
}
