import { useVideoStore } from '../../stores/videoStore'

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

export default function VideoEditor() {
  const { aspectRatio, setAspectRatio, aiProvider, setAiProvider, ttsProvider, setTtsProvider } =
    useVideoStore()

  return (
    <div className="space-y-6">
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
