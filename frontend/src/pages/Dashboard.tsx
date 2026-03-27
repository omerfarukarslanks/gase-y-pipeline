import { Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  PlusCircle, Video, Eye, ThumbsUp, Share2,
  TrendingUp, Calendar, ExternalLink, Loader2,
} from 'lucide-react'
import { analyticsApi } from '../api/analytics'
import { useProjects } from '../hooks/useVideo'

export default function Dashboard() {
  const { data: overview, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => analyticsApi.overview(),
    select: (res) => res.data,
  })

  const { data: topPerforming = [] } = useQuery({
    queryKey: ['top-performing'],
    queryFn: () => analyticsApi.topPerforming(3),
    select: (res) => res.data,
  })

  const { data: projects = [], isLoading: projectsLoading } = useProjects(1)

  const stats = [
    {
      label: 'Total Videos',
      value: overview?.total_videos || 0,
      icon: Video,
      color: 'bg-blue-50 text-blue-600',
    },
    {
      label: 'Total Views',
      value: overview?.total_views || 0,
      icon: Eye,
      color: 'bg-green-50 text-green-600',
    },
    {
      label: 'Total Likes',
      value: overview?.total_likes || 0,
      icon: ThumbsUp,
      color: 'bg-purple-50 text-purple-600',
    },
    {
      label: 'Published',
      value: overview?.total_published || 0,
      icon: Share2,
      color: 'bg-orange-50 text-orange-600',
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-sm text-gray-500">Welcome to Gase-Y Pipeline</p>
        </div>
        <Link
          to="/create"
          className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-brand-700"
        >
          <PlusCircle className="h-4 w-4" />
          Create Video
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="rounded-xl border border-gray-200 bg-white p-5">
            <div className="flex items-center gap-3">
              <div className={`rounded-lg p-2.5 ${stat.color}`}>
                <stat.icon className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs text-gray-500">{stat.label}</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatNumber(stat.value)}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Projects */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-sm font-medium text-gray-700">Recent Projects</h3>
            <Link to="/videos" className="text-xs text-brand-600 hover:underline">View all</Link>
          </div>

          {projectsLoading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin text-gray-300" />
            </div>
          ) : projects.length === 0 ? (
            <div className="py-8 text-center">
              <Video className="mx-auto h-10 w-10 text-gray-300" />
              <p className="mt-2 text-sm text-gray-500">No videos yet</p>
              <Link
                to="/create"
                className="mt-3 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline"
              >
                <PlusCircle className="h-3.5 w-3.5" />
                Create your first video
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {projects.slice(0, 5).map((project) => (
                <Link
                  key={project.id}
                  to={`/videos/${project.id}`}
                  className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2.5 text-sm transition-colors hover:bg-gray-100"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-gray-900 truncate">{project.title}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(project.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <StatusDot status={project.status} />
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Top Performing */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="flex items-center gap-1.5 text-sm font-medium text-gray-700">
              <TrendingUp className="h-4 w-4" />
              Top Performing
            </h3>
            <Link to="/analytics" className="text-xs text-brand-600 hover:underline">
              Full analytics
            </Link>
          </div>

          {topPerforming.length === 0 ? (
            <div className="py-8 text-center">
              <TrendingUp className="mx-auto h-10 w-10 text-gray-300" />
              <p className="mt-2 text-sm text-gray-500">Publish videos to see performance</p>
            </div>
          ) : (
            <div className="space-y-2">
              {topPerforming.map((item, i) => (
                <div key={item.job_id} className="flex items-center gap-3 rounded-lg bg-gray-50 px-3 py-2.5">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.title || 'Untitled'}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="capitalize">{item.platform}</span>
                      <span>{formatNumber(item.views)} views</span>
                      <span>{formatNumber(item.likes)} likes</span>
                    </div>
                  </div>
                  {item.platform_url && (
                    <a
                      href={item.platform_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-brand-500 hover:text-brand-600"
                    >
                      <ExternalLink className="h-4 w-4" />
                    </a>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <QuickAction to="/create" icon={PlusCircle} label="Create Video" color="bg-brand-50 text-brand-600" />
        <QuickAction to="/templates" icon={Video} label="Templates" color="bg-blue-50 text-blue-600" />
        <QuickAction to="/calendar" icon={Calendar} label="Calendar" color="bg-amber-50 text-amber-600" />
        <QuickAction to="/accounts" icon={Share2} label="Accounts" color="bg-green-50 text-green-600" />
      </div>
    </div>
  )
}

function StatusDot({ status }: { status: string }) {
  const colors: Record<string, string> = {
    draft: 'bg-gray-400',
    processing: 'bg-amber-400',
    ready: 'bg-green-400',
    published: 'bg-blue-400',
    failed: 'bg-red-400',
  }
  return (
    <span
      className={`h-2.5 w-2.5 rounded-full ${colors[status] || 'bg-gray-300'}`}
      title={status}
    />
  )
}

function QuickAction({
  to, icon: Icon, label, color,
}: {
  to: string; icon: React.ElementType; label: string; color: string
}) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-4 transition-shadow hover:shadow-sm"
    >
      <div className={`rounded-lg p-2 ${color}`}>
        <Icon className="h-4 w-4" />
      </div>
      <span className="text-sm font-medium text-gray-700">{label}</span>
    </Link>
  )
}

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return num.toString()
}
