import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { AlertCircle } from 'lucide-react'
import { useVideoStore } from '../../stores/videoStore'
import { platformsApi } from '../../api/platforms'

const PLATFORMS = [
  { id: 'youtube', name: 'YouTube', color: 'bg-red-500' },
  { id: 'instagram', name: 'Instagram', color: 'bg-pink-500' },
  { id: 'twitter', name: 'Twitter/X', color: 'bg-sky-500' },
  { id: 'tiktok', name: 'TikTok', color: 'bg-gray-900' },
  { id: 'reddit', name: 'Reddit', color: 'bg-orange-500' },
]

export default function PlatformSelector() {
  const { selectedPlatforms, setSelectedPlatforms } = useVideoStore()

  const { data: accounts = [] } = useQuery({
    queryKey: ['platform-accounts'],
    queryFn: () => platformsApi.list(),
    select: (res) => res.data,
  })

  const connectedPlatforms = new Set(
    accounts.filter((a) => a.is_active).map((a) => a.platform)
  )

  const togglePlatform = (id: string) => {
    if (!connectedPlatforms.has(id)) return
    if (selectedPlatforms.includes(id)) {
      setSelectedPlatforms(selectedPlatforms.filter((p) => p !== id))
    } else {
      setSelectedPlatforms([...selectedPlatforms, id])
    }
  }

  const hasNoConnections = connectedPlatforms.size === 0

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Publish To</label>

      {hasNoConnections && (
        <div className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
          <AlertCircle className="h-4 w-4 flex-shrink-0" />
          <span>
            No connected accounts.{' '}
            <Link to="/accounts" className="font-medium underline">
              Connect a platform
            </Link>{' '}
            to enable publishing.
          </span>
        </div>
      )}

      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((platform) => {
          const isConnected = connectedPlatforms.has(platform.id)
          const isSelected = selectedPlatforms.includes(platform.id)

          return (
            <button
              key={platform.id}
              onClick={() => togglePlatform(platform.id)}
              disabled={!isConnected}
              className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
                isSelected && isConnected
                  ? `${platform.color} text-white shadow-md`
                  : isConnected
                    ? 'border border-gray-200 bg-white text-gray-600 hover:border-gray-300'
                    : 'border border-gray-100 bg-gray-50 text-gray-400 cursor-not-allowed'
              }`}
              title={isConnected ? platform.name : `Connect ${platform.name} first`}
            >
              {platform.name}
              {!isConnected && (
                <span className="text-[10px] text-gray-400">(not connected)</span>
              )}
            </button>
          )
        })}
      </div>
    </div>
  )
}
