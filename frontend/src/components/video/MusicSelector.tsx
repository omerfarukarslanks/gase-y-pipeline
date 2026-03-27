import { useQuery } from '@tanstack/react-query'
import { Music, Volume2, VolumeX } from 'lucide-react'
import { useVideoStore } from '../../stores/videoStore'
import { mediaApi } from '../../api/media'

const MOOD_LABELS: Record<string, string> = {
  upbeat: 'Upbeat',
  calm: 'Calm',
  inspiring: 'Inspiring',
  energetic: 'Energetic',
  professional: 'Professional',
  warm: 'Warm',
  dramatic: 'Dramatic',
  happy: 'Happy',
}

export default function MusicSelector() {
  const { bgMusic, setBgMusic } = useVideoStore()

  const { data: tracks = [] } = useQuery({
    queryKey: ['music-tracks'],
    queryFn: () => mediaApi.listTracks(),
    select: (res) => res.data,
  })

  const formatDuration = (sec: number) => {
    const m = Math.floor(sec / 60)
    const s = sec % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="block text-sm font-medium text-gray-700">
          <Music className="mr-1.5 inline h-4 w-4" />
          Background Music
        </label>
        {bgMusic && (
          <button
            onClick={() => setBgMusic(null)}
            className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
          >
            <VolumeX className="h-3.5 w-3.5" />
            No music
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
        {tracks.map((track) => (
          <button
            key={track.id}
            onClick={() => setBgMusic(track.id === bgMusic ? null : track.id)}
            disabled={!track.available}
            className={`rounded-lg border p-3 text-left text-sm transition-all ${
              bgMusic === track.id
                ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-500'
                : track.available
                  ? 'border-gray-200 hover:border-gray-300'
                  : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
            }`}
          >
            <div className="flex items-center gap-2">
              {bgMusic === track.id ? (
                <Volume2 className="h-4 w-4 text-brand-600 flex-shrink-0" />
              ) : (
                <Music className="h-4 w-4 text-gray-400 flex-shrink-0" />
              )}
              <span className="font-medium text-gray-900 truncate text-xs">
                {track.name}
              </span>
            </div>
            <div className="mt-1 flex items-center justify-between text-[10px] text-gray-500">
              <span className="capitalize">
                {MOOD_LABELS[track.mood] || track.mood}
              </span>
              <span>{formatDuration(track.duration_sec)}</span>
            </div>
          </button>
        ))}
      </div>

      {tracks.length === 0 && (
        <p className="text-xs text-gray-400 text-center py-4">
          No music tracks available. Add tracks to the music library to enable background music.
        </p>
      )}
    </div>
  )
}
