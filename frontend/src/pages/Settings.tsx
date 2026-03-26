import { Settings as SettingsIcon } from 'lucide-react'

export default function Settings() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Settings</h1>

      <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-6">
        <h2 className="text-lg font-medium text-gray-900">Default AI Providers</h2>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Script Generation</label>
            <select className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="openai">OpenAI GPT</option>
              <option value="claude">Anthropic Claude</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">Text-to-Speech</label>
            <select className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm">
              <option value="elevenlabs">ElevenLabs</option>
              <option value="google_tts">Google TTS</option>
            </select>
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6 space-y-6">
        <h2 className="text-lg font-medium text-gray-900">API Keys</h2>
        <p className="text-sm text-gray-500">
          Configure your API keys for external services. These are stored securely.
        </p>

        <div className="space-y-4">
          {['OpenAI', 'Anthropic', 'ElevenLabs', 'Stability AI', 'DeepL'].map((service) => (
            <div key={service} className="space-y-1">
              <label className="block text-sm font-medium text-gray-700">{service} API Key</label>
              <input
                type="password"
                placeholder="sk-..."
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm"
              />
            </div>
          ))}
        </div>

        <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700">
          Save Settings
        </button>
      </div>
    </div>
  )
}
