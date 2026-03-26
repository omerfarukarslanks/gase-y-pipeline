import { Share2, ExternalLink } from 'lucide-react'

const platforms = [
  { id: 'youtube', name: 'YouTube', color: 'bg-red-500', connected: false },
  { id: 'instagram', name: 'Instagram', color: 'bg-pink-500', connected: false },
  { id: 'twitter', name: 'Twitter/X', color: 'bg-sky-500', connected: false },
  { id: 'tiktok', name: 'TikTok', color: 'bg-gray-900', connected: false },
  { id: 'reddit', name: 'Reddit', color: 'bg-orange-500', connected: false },
]

export default function SocialAccounts() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Social Accounts</h1>
        <p className="text-sm text-gray-500">Connect your social media accounts for publishing</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {platforms.map((platform) => (
          <div
            key={platform.id}
            className="rounded-xl border border-gray-200 bg-white p-6"
          >
            <div className="flex items-center gap-3">
              <div className={`h-10 w-10 rounded-lg ${platform.color} flex items-center justify-center`}>
                <Share2 className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">{platform.name}</h3>
                <p className="text-xs text-gray-500">
                  {platform.connected ? 'Connected' : 'Not connected'}
                </p>
              </div>
            </div>

            <button
              className={`mt-4 flex w-full items-center justify-center gap-2 rounded-lg py-2 text-sm font-medium ${
                platform.connected
                  ? 'border border-red-200 text-red-600 hover:bg-red-50'
                  : 'border border-gray-200 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {platform.connected ? (
                'Disconnect'
              ) : (
                <>
                  <ExternalLink className="h-4 w-4" />
                  Connect
                </>
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
