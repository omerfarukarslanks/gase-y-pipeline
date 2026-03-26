import { useQuery } from '@tanstack/react-query'
import { Info } from 'lucide-react'
import { useVideoStore } from '../../stores/videoStore'
import { platformsApi } from '../../api/platforms'

const ASPECT_RATIOS = [
  { value: '16:9', label: '16:9 (YouTube)', desc: 'Landscape' },
  { value: '9:16', label: '9:16 (Reels/Shorts)', desc: 'Portrait' },
  { value: '1:1', label: '1:1 (Square)', desc: 'Instagram' },
]

const AI_PROVIDERS = [
  { value: 'openai', label: 'OpenAI GPT' },
  { value: 'claude', label: 'Anthropic Claude' },
]

const TTS_PROVIDERS = [
  { value: 'elevenlabs', label: 'ElevenLabs' },
  { value: 'google_tts', label: 'Google TTS' },
]

// Platform-specific recommended format presets
const PLATFORM_PRESETS: Record<string, { aspect: string; label: string }> = {
  youtube: { aspect: '16:9', label: 'YouTube (16:9 Landscape)' },
  instagram: { aspect: '9:16', label: 'Instagram Reels (9:16 Portrait)' },
  tiktok: { aspect: '9:16', label: 'TikTok (9:16 Portrait)' },
  twitter: { aspect: '16:9', label: 'Twitter/X (16:9 Landscape)' },
  reddit: { aspect: '16:9', label: 'Reddit (16:9 Landscape)' },
}

export default function VideoEditor() {
  const {
    aspectRatio, setAspectRatio,
    aiProvider, setAiProvider,
    ttsProvider, setTtsProvider,
    selectedPlatforms,
  } = useVideoStore()

  const { data: accounts = [] } = useQuery({
    queryKey: ['platform-accounts'],
    queryFn: () => platformsApi.list(),
    select: (res) => res.data,
  })

  const connectedPlatforms = new Set(
    accounts.filter((a) => a.is_active).map((a) => a.platform)
  )

  // Get recommended aspect ratio from selected platforms
  const getRecommendedAspect = (): string | null => {
    const active = selectedPlatforms.filter((p) => connectedPlatforms.has(p))
    if (active.length === 0) return null

    // If all selected platforms prefer the same aspect ratio, recommend it
    const aspects = active.map((p) => PLATFORM_PRESETS[p]?.aspect).filter(Boolean)
    const unique = [...new Set(aspects)]
    if (unique.length === 1) return unique[0]
    return null
  }

  const recommended = getRecommendedAspect()

  return (
    <div className="space-y-6">
      {/* Platform-specific presets */}
      {selectedPlatforms.length > 0 && (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Platform Presets</label>
          <div className="flex flex-wrap gap-2">
            {selectedPlatforms
              .filter((p) => PLATFORM_PRESETS[p])
              .map((p) => {
                const preset = PLATFORM_PRESETS[p]
                return (
                  <button
                    key={p}
                    onClick={() => setAspectRatio(preset.aspect)}
                    className={`rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
                      aspectRatio === preset.aspect
                        ? 'border-brand-500 bg-brand-50 text-brand-700'
                        : 'border-gray-200 text-gray-600 hover:border-gray-300'
                    }`}
                  >
                    {preset.label}
                  </button>
                )
              })}
          </div>
          {recommended && recommended !== aspectRatio && (
            <p className="flex items-center gap-1 text-xs text-amber-600">
              <Info className="h-3 w-3" />
              Recommended: {recommended} for your selected platforms
            </p>
          )}
        </div>
      )}

      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">Aspect Ratio</label>
        <div className="grid grid-cols-3 gap-2">
          {ASPECT_RATIOS.map((ratio) => (
            <button
              key={ratio.value}
              onClick={() => setAspectRatio(ratio.value)}
              className={`rounded-lg border p-3 text-center transition-all ${
                aspectRatio === ratio.value
                  ? 'border-brand-500 bg-brand-50 text-brand-700'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="text-sm font-medium">{ratio.label}</div>
              <div className="text-xs text-gray-500">{ratio.desc}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">AI Provider</label>
          <select
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
          >
            {AI_PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>

        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">TTS Provider</label>
          <select
            value={ttsProvider}
            onChange={(e) => setTtsProvider(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
          >
            {TTS_PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  )
}
