import ReactPlayer from 'react-player'
import StatusBadge from '../common/StatusBadge'

interface VideoPreviewProps {
  url?: string | null
  status: string
  title?: string
}

export default function VideoPreview({ url, status, title }: VideoPreviewProps) {
  return (
    <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
      <div className="aspect-video bg-gray-900 flex items-center justify-center">
        {url ? (
          <ReactPlayer url={url} controls width="100%" height="100%" />
        ) : (
          <div className="text-center text-gray-400">
            <p className="text-sm">
              {status === 'pending'
                ? 'Video is being generated...'
                : status === 'processing'
                ? 'Processing video...'
                : 'No preview available'}
            </p>
          </div>
        )}
      </div>
      {title && (
        <div className="flex items-center justify-between p-4">
          <p className="text-sm font-medium text-gray-900">{title}</p>
          <StatusBadge status={status} />
        </div>
      )}
    </div>
  )
}
