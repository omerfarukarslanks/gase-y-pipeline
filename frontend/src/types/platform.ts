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
  platform_account_id: string
  platform: string
  status: 'pending' | 'scheduled' | 'publishing' | 'published' | 'failed'
  scheduled_at: string | null
  published_at: string | null
  platform_url: string | null
  platform_post_id: string | null
  error_message: string | null
  metadata: Record<string, unknown> | null
  created_at: string
}

export interface PlatformPublishMetadata {
  title?: string
  description?: string
  tags?: string[]
}

export interface PublishRequest {
  video_variant_id: string
  platform_account_ids: string[]
  scheduled_at?: string
  platform_metadata?: Record<string, PlatformPublishMetadata>
}

export interface MultiVariantPublishRequest {
  variant_ids: string[]
  platform_account_ids: string[]
  scheduled_at?: string
}

export interface PromptHistoryEntry {
  id: string
  prompt_text: string
  project_id: string | null
  is_favorite: boolean
  created_at: string
}
