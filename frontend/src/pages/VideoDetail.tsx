import { useParams } from 'react-router-dom'
import LoadingSpinner from '../components/common/LoadingSpinner'
import StatusBadge from '../components/common/StatusBadge'
import { useProject } from '../hooks/useVideo'

export default function VideoDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: project, isLoading } = useProject(id!)

  if (isLoading) {
    return (
      <div className="py-12">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!project) {
    return <div className="text-center text-gray-500">Project not found</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{project.title}</h1>
          <p className="mt-1 text-sm text-gray-500">{project.original_prompt}</p>
        </div>
        <StatusBadge status={project.status} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <div className="aspect-video rounded-xl bg-gray-900 flex items-center justify-center">
            <p className="text-gray-400">Video preview</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h3 className="text-sm font-medium text-gray-700">Details</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Status</dt>
                <dd><StatusBadge status={project.status} /></dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Created</dt>
                <dd className="text-gray-900">
                  {new Date(project.created_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>

          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h3 className="text-sm font-medium text-gray-700">Language Variants</h3>
            <p className="mt-2 text-sm text-gray-500">
              Variants will appear here after generation.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
