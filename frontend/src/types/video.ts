export interface Project {
  id: string
  title: string
  original_prompt: string
  analyzed_content: Record<string, unknown> | null
  template_id: string | null
  status: 'draft' | 'processing' | 'ready' | 'published' | 'failed'
  settings: Record<string, unknown>
  created_at: string
}

export interface Video {
  id: string
  project_id: string
  aspect_ratio: string
  resolution: string
  duration_sec: number | null
  thumbnail_url: string | null
  status: string
  created_at: string
}

export interface VideoVariant {
  id: string
  video_id: string
  language: string
  file_url: string | null
  title: string | null
  description: string | null
  hashtags: string[] | null
  status: string
  created_at: string
}

export interface Template {
  id: string
  name: string
  category: string | null
  description: string | null
  scene_structure: Record<string, unknown>
  default_settings: Record<string, unknown>
  is_system: boolean
  created_at: string
}

export interface VideoGenerateRequest {
  project_id: string
  languages: string[]
  aspect_ratio: string
  resolution: string
  ai_provider: string
  tts_provider: string
}
