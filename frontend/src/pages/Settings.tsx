import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Save, User, Key, Sliders, Loader2, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

interface UserPreferences {
  default_ai_provider?: string
  default_tts_provider?: string
  default_image_provider?: string
  default_languages?: string[]
  default_platforms?: string[]
  api_keys?: {
    openai?: string
    anthropic?: string
    elevenlabs?: string
    stability?: string
    deepl?: string
  }
}

export default function Settings() {
  const { user, setUser } = useAuthStore()
  const queryClient = useQueryClient()

  const prefs = (user?.preferences || {}) as UserPreferences

  // Profile
  const [fullName, setFullName] = useState(user?.full_name || '')

  // Default providers
  const [aiProvider, setAiProvider] = useState(prefs.default_ai_provider || 'openai')
  const [ttsProvider, setTtsProvider] = useState(prefs.default_tts_provider || 'elevenlabs')
  const [imageProvider, setImageProvider] = useState(prefs.default_image_provider || 'dalle')

  // API Keys (masked display)
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({
    openai: prefs.api_keys?.openai || '',
    anthropic: prefs.api_keys?.anthropic || '',
    elevenlabs: prefs.api_keys?.elevenlabs || '',
    stability: prefs.api_keys?.stability || '',
    deepl: prefs.api_keys?.deepl || '',
  })

  const [saved, setSaved] = useState(false)

  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '')
      const p = (user.preferences || {}) as UserPreferences
      setAiProvider(p.default_ai_provider || 'openai')
      setTtsProvider(p.default_tts_provider || 'elevenlabs')
      setImageProvider(p.default_image_provider || 'dalle')
      setApiKeys({
        openai: p.api_keys?.openai || '',
        anthropic: p.api_keys?.anthropic || '',
        elevenlabs: p.api_keys?.elevenlabs || '',
        stability: p.api_keys?.stability || '',
        deepl: p.api_keys?.deepl || '',
      })
    }
  }, [user])

  const profileMutation = useMutation({
    mutationFn: () => authApi.updateMe({ full_name: fullName }),
    onSuccess: (res) => {
      setUser(res.data)
      toast.success('Profile updated')
    },
    onError: () => toast.error('Failed to update profile'),
  })

  const preferencesMutation = useMutation({
    mutationFn: () => {
      const newPrefs: UserPreferences = {
        default_ai_provider: aiProvider,
        default_tts_provider: ttsProvider,
        default_image_provider: imageProvider,
        api_keys: apiKeys,
      }
      return authApi.updateMe({ preferences: newPrefs })
    },
    onSuccess: (res) => {
      setUser(res.data)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
      toast.success('Settings saved')
    },
    onError: () => toast.error('Failed to save settings'),
  })

  const handleApiKeyChange = (key: string, value: string) => {
    setApiKeys((prev) => ({ ...prev, [key]: value }))
  }

  const API_KEY_FIELDS = [
    { id: 'openai', label: 'OpenAI', placeholder: 'sk-...' },
    { id: 'anthropic', label: 'Anthropic', placeholder: 'sk-ant-...' },
    { id: 'elevenlabs', label: 'ElevenLabs', placeholder: 'xi-...' },
    { id: 'stability', label: 'Stability AI', placeholder: 'sk-...' },
    { id: 'deepl', label: 'DeepL', placeholder: 'deepl-...' },
  ]

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      {/* Profile */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
        <h2 className="flex items-center gap-2 text-lg font-medium text-gray-900">
          <User className="h-5 w-5 text-gray-500" />
          Profile
        </h2>

        <div className="space-y-4">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Email</label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full rounded-lg border border-gray-200 bg-gray-50 px-3 py-2 text-sm text-gray-500"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
              placeholder="Your name"
            />
          </div>

          <button
            onClick={() => profileMutation.mutate()}
            disabled={profileMutation.isPending}
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50"
          >
            {profileMutation.isPending ? 'Saving...' : 'Update Profile'}
          </button>
        </div>
      </div>

      {/* Default Providers */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
        <h2 className="flex items-center gap-2 text-lg font-medium text-gray-900">
          <Sliders className="h-5 w-5 text-gray-500" />
          Default Providers
        </h2>
        <p className="text-sm text-gray-500">
          Set defaults for new video projects. Can be overridden per project.
        </p>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Script Generation</label>
            <select
              value={aiProvider}
              onChange={(e) => setAiProvider(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
            >
              <option value="openai">OpenAI GPT</option>
              <option value="claude">Anthropic Claude</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Text-to-Speech</label>
            <select
              value={ttsProvider}
              onChange={(e) => setTtsProvider(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
            >
              <option value="elevenlabs">ElevenLabs</option>
              <option value="google_tts">Google TTS</option>
            </select>
          </div>

          <div className="space-y-1">
            <label className="block text-sm font-medium text-gray-700">Image Generation</label>
            <select
              value={imageProvider}
              onChange={(e) => setImageProvider(e.target.value)}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
            >
              <option value="dalle">DALL-E 3</option>
              <option value="stability">Stability AI</option>
            </select>
          </div>
        </div>
      </div>

      {/* API Keys */}
      <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-4">
        <h2 className="flex items-center gap-2 text-lg font-medium text-gray-900">
          <Key className="h-5 w-5 text-gray-500" />
          API Keys
        </h2>
        <p className="text-sm text-gray-500">
          Configure API keys for external services. Keys are stored in your user preferences.
        </p>

        <div className="space-y-3">
          {API_KEY_FIELDS.map((field) => (
            <div key={field.id} className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">
                {field.label} API Key
              </label>
              <input
                type="password"
                value={apiKeys[field.id] || ''}
                onChange={(e) => handleApiKeyChange(field.id, e.target.value)}
                placeholder={field.placeholder}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
              />
            </div>
          ))}
        </div>
      </div>

      {/* Save All */}
      <button
        onClick={() => preferencesMutation.mutate()}
        disabled={preferencesMutation.isPending}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-brand-600 py-3 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
      >
        {preferencesMutation.isPending ? (
          <><Loader2 className="h-4 w-4 animate-spin" /> Saving...</>
        ) : saved ? (
          <><CheckCircle className="h-4 w-4" /> Saved!</>
        ) : (
          <><Save className="h-4 w-4" /> Save All Settings</>
        )}
      </button>
    </div>
  )
}
