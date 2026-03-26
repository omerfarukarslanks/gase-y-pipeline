import { useVideoStore } from '../../stores/videoStore'

const PLATFORMS = [
  { id: 'youtube', name: 'YouTube', color: 'bg-red-500' },
  { id: 'instagram', name: 'Instagram', color: 'bg-pink-500' },
  { id: 'twitter', name: 'Twitter/X', color: 'bg-sky-500' },
  { id: 'tiktok', name: 'TikTok', color: 'bg-gray-900' },
  { id: 'reddit', name: 'Reddit', color: 'bg-orange-500' },
]

export default function PlatformSelector() {
  const { selectedPlatforms, setSelectedPlatforms } = useVideoStore()

  const togglePlatform = (id: string) => {
    if (selectedPlatforms.includes(id)) {
      setSelectedPlatforms(selectedPlatforms.filter((p) => p !== id))
    } else {
      setSelectedPlatforms([...selectedPlatforms, id])
    }
  }

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">Publish To</label>
      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((platform) => (
          <button
            key={platform.id}
            onClick={() => togglePlatform(platform.id)}
            className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              selectedPlatforms.includes(platform.id)
                ? `${platform.color} text-white shadow-md`
                : 'border border-gray-200 bg-white text-gray-600 hover:border-gray-300'
            }`}
          >
            {platform.name}
          </button>
        ))}
      </div>
    </div>
  )
}
