import { useQuery } from '@tanstack/react-query'
import {
  BarChart3, Eye, ThumbsUp, MessageSquare, Share2,
  ExternalLink, TrendingUp, Loader2,
} from 'lucide-react'
import { analyticsApi } from '../api/analytics'
import type { AnalyticsOverview, TopPerforming } from '../api/analytics'

const PLATFORM_COLORS: Record<string, string> = {
  youtube: 'bg-red-100 text-red-700',
  instagram: 'bg-pink-100 text-pink-700',
  twitter: 'bg-sky-100 text-sky-700',
  tiktok: 'bg-gray-100 text-gray-700',
  reddit: 'bg-orange-100 text-orange-700',
}

export default function Analytics() {
  const { data: overview, isLoading } = useQuery({
    queryKey: ['analytics-overview'],
    queryFn: () => analyticsApi.overview(),
    select: (res) => res.data,
  })

  const { data: topPerforming = [] } = useQuery({
    queryKey: ['top-performing'],
    queryFn: () => analyticsApi.topPerforming(5),
    select: (res) => res.data,
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
      </div>
    )
  }

  const hasData = overview && (overview.total_published > 0 || overview.total_views > 0)

  if (!hasData) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
          <BarChart3 className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No analytics data yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Analytics will appear here after you publish videos to social platforms.
          </p>
        </div>
      </div>
    )
  }

  const stats = [
    { label: 'Total Views', value: overview!.total_views, icon: Eye, color: 'bg-blue-50 text-blue-600' },
    { label: 'Total Likes', value: overview!.total_likes, icon: ThumbsUp, color: 'bg-green-50 text-green-600' },
    { label: 'Total Comments', value: overview!.total_comments, icon: MessageSquare, color: 'bg-purple-50 text-purple-600' },
    { label: 'Total Shares', value: overview!.total_shares, icon: Share2, color: 'bg-orange-50 text-orange-600' },
  ]

  const platforms = Object.entries(overview!.platforms)

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500">
          {overview!.total_published} videos published across {platforms.length} platform{platforms.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Stats cards */}
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
        {/* Platform breakdown */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h3 className="mb-4 text-sm font-medium text-gray-700">Platform Breakdown</h3>
          {platforms.length === 0 ? (
            <p className="text-sm text-gray-400">No platform data</p>
          ) : (
            <div className="space-y-3">
              {platforms.map(([platform, data]) => {
                const maxViews = Math.max(...platforms.map(([, d]) => d.views), 1)
                const pct = (data.views / maxViews) * 100
                return (
                  <div key={platform}>
                    <div className="flex items-center justify-between text-sm">
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${PLATFORM_COLORS[platform] || 'bg-gray-100 text-gray-600'}`}>
                        {platform}
                      </span>
                      <span className="text-gray-500">
                        {formatNumber(data.views)} views / {formatNumber(data.likes)} likes
                      </span>
                    </div>
                    <div className="mt-1.5 h-2 rounded-full bg-gray-100">
                      <div
                        className="h-2 rounded-full bg-brand-500 transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        {/* Top performing */}
        <div className="rounded-xl border border-gray-200 bg-white p-5">
          <h3 className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
            <TrendingUp className="h-4 w-4" />
            Top Performing
          </h3>
          {topPerforming.length === 0 ? (
            <p className="text-sm text-gray-400">No published videos yet</p>
          ) : (
            <div className="space-y-3">
              {topPerforming.map((item, i) => (
                <div key={item.job_id} className="flex items-center gap-3 rounded-lg bg-gray-50 px-3 py-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-brand-100 text-xs font-bold text-brand-700">
                    {i + 1}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {item.title || 'Untitled'}
                    </p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <span className="capitalize">{item.platform}</span>
                      <span>{item.language.toUpperCase()}</span>
                      <span>{formatNumber(item.views)} views</span>
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
    </div>
  )
}

function formatNumber(num: number): string {
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(1)}M`
  if (num >= 1_000) return `${(num / 1_000).toFixed(1)}K`
  return num.toString()
}
