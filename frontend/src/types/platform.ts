export interface PlatformAccount {
  id: string
  platform: 'youtube' | 'instagram' | 'twitter' | 'reddit' | 'tiktok'
  display_name: string | null
  is_active: boolean
  created_at: string
}

export interface PublishJob {
  id: string
  video_variant_id: string
  platform: string
  status: 'pending' | 'scheduled' | 'publishing' | 'published' | 'failed'
  scheduled_at: string | null
  published_at: string | null
  platform_url: string | null
  error_message: string | null
  created_at: string
}

export interface PublishRequest {
  video_variant_id: string
  platform_account_ids: string[]
  scheduled_at?: string
}
