import { Link } from 'react-router-dom'
import { PlusCircle } from 'lucide-react'
import StatusBadge from '../components/common/StatusBadge'
import LoadingSpinner from '../components/common/LoadingSpinner'
import { useProjects } from '../hooks/useVideo'

export default function MyVideos() {
  const { data: projects, isLoading } = useProjects()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Videos</h1>
        <Link
          to="/create"
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          <PlusCircle className="h-4 w-4" />
          New Video
        </Link>
      </div>

      {isLoading ? (
        <div className="py-12">
          <LoadingSpinner size="lg" />
        </div>
      ) : !projects?.length ? (
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <p className="text-gray-500">No videos yet. Create your first one!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/videos/${project.id}`}
              className="rounded-xl border border-gray-200 bg-white p-5 transition-shadow hover:shadow-md"
            >
              <div className="mb-3 aspect-video rounded-lg bg-gray-100" />
              <h3 className="text-sm font-medium text-gray-900 line-clamp-1">
                {project.title}
              </h3>
              <p className="mt-1 text-xs text-gray-500 line-clamp-2">
                {project.original_prompt}
              </p>
              <div className="mt-3 flex items-center justify-between">
                <StatusBadge status={project.status} />
                <span className="text-xs text-gray-400">
                  {new Date(project.created_at).toLocaleDateString()}
                </span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
