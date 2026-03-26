import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Play, Globe, Send, RefreshCw, CheckCircle, XCircle,
  Clock, Loader2, ExternalLink, ChevronDown, ChevronUp,
} from 'lucide-react'
import { toast } from 'sonner'
import LoadingSpinner from '../components/common/LoadingSpinner'
import StatusBadge from '../components/common/StatusBadge'
import { useProject } from '../hooks/useVideo'
import { videosApi } from '../api/videos'
import { platformsApi } from '../api/platforms'
import type { VideoVariant } from '../types/video'
import type { PlatformAccount, PublishJob } from '../types/platform'

const LANGUAGE_NAMES: Record<string, string> = {
  en: 'English', tr: 'Turkish', de: 'German', fr: 'French',
  es: 'Spanish', ja: 'Japanese', ko: 'Korean', zh: 'Chinese',
  ar: 'Arabic', pt: 'Portuguese', ru: 'Russian', it: 'Italian',
}

const PLATFORM_COLORS: Record<string, string> = {
  youtube: 'bg-red-500', instagram: 'bg-pink-500', twitter: 'bg-sky-500',
  tiktok: 'bg-gray-900', reddit: 'bg-orange-500',
}

export default function VideoDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [selectedVariant, setSelectedVariant] = useState<VideoVariant | null>(null)
  const [showPublish, setShowPublish] = useState(false)
  const [selectedAccounts, setSelectedAccounts] = useState<string[]>([])
  const [publishExpanded, setPublishExpanded] = useState(false)

  const { data: project, isLoading: projectLoading } = useProject(id!)

  // Fetch video for this project
  const { data: video } = useQuery({
    queryKey: ['project-video', id],
    queryFn: async () => {
      // Get project's videos (the project_id is used to find the video)
      const res = await videosApi.get(id!)
      return res.data
    },
    enabled: !!id && !!project,
    retry: false,
  })

  // Fetch variants
  const { data: variants = [] } = useQuery({
    queryKey: ['video-variants', video?.id],
    queryFn: () => videosApi.getVariants(video!.id),
    select: (res) => res.data,
    enabled: !!video?.id,
  })

  // Fetch connected accounts
  const { data: accounts = [] } = useQuery({
    queryKey: ['platform-accounts'],
    queryFn: () => platformsApi.list(),
    select: (res) => res.data,
  })

  // Fetch publish jobs
  const { data: publishJobs = [] } = useQuery({
    queryKey: ['publish-jobs', id],
    queryFn: () => platformsApi.listJobs({ page: 1 }),
    select: (res) => res.data,
    enabled: !!id,
  })

  const publishMutation = useMutation({
    mutationFn: (data: { variant_id: string; account_ids: string[] }) =>
      platformsApi.publish({
        video_variant_id: data.variant_id,
        platform_account_ids: data.account_ids,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publish-jobs'] })
      toast.success('Publishing started!')
      setShowPublish(false)
      setSelectedAccounts([])
    },
    onError: () => toast.error('Failed to start publishing'),
  })

  const retryMutation = useMutation({
    mutationFn: (jobId: string) => platformsApi.retryJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publish-jobs'] })
      toast.success('Retrying publish...')
    },
  })

  if (projectLoading) {
    return <div className="py-12"><LoadingSpinner size="lg" /></div>
  }

  if (!project) {
    return <div className="text-center text-gray-500">Project not found</div>
  }

  const activeAccounts = accounts.filter((a) => a.is_active)
  const completedVariants = variants.filter((v) => v.status === 'completed')

  const toggleAccount = (accountId: string) => {
    setSelectedAccounts((prev) =>
      prev.includes(accountId)
        ? prev.filter((id) => id !== accountId)
        : [...prev, accountId]
    )
  }

  const handlePublish = () => {
    if (!selectedVariant || selectedAccounts.length === 0) return
    publishMutation.mutate({
      variant_id: selectedVariant.id,
      account_ids: selectedAccounts,
    })
  }

  const getJobStatusIcon = (status: string) => {
    switch (status) {
      case 'published': return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />
      case 'publishing': return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />
      case 'scheduled': return <Clock className="h-4 w-4 text-amber-500" />
      default: return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  // Filter jobs related to this video's variants
  const variantIds = new Set(variants.map((v) => v.id))
  const relatedJobs = publishJobs.filter((j) => variantIds.has(j.video_variant_id))

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{project.title}</h1>
          <p className="mt-1 text-sm text-gray-500">{project.original_prompt}</p>
        </div>
        <StatusBadge status={project.status} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Video Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="aspect-video rounded-xl bg-gray-900 flex items-center justify-center overflow-hidden">
            {selectedVariant?.file_url ? (
              <video
                src={selectedVariant.file_url}
                controls
                className="h-full w-full object-contain"
              />
            ) : completedVariants.length > 0 && completedVariants[0].file_url ? (
              <video
                src={completedVariants[0].file_url}
                controls
                className="h-full w-full object-contain"
              />
            ) : (
              <div className="text-center">
                <Play className="mx-auto h-12 w-12 text-gray-600" />
                <p className="mt-2 text-sm text-gray-400">
                  {project.status === 'processing'
                    ? 'Video is being generated...'
                    : 'No video available'}
                </p>
              </div>
            )}
          </div>

          {/* Variant selector */}
          {variants.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-4">
              <h3 className="mb-3 text-sm font-medium text-gray-700">
                <Globe className="mr-1.5 inline h-4 w-4" />
                Language Variants ({variants.length})
              </h3>
              <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
                {variants.map((variant) => (
                  <button
                    key={variant.id}
                    onClick={() => setSelectedVariant(variant)}
                    className={`flex items-center justify-between rounded-lg border p-3 text-left text-sm transition-all ${
                      selectedVariant?.id === variant.id
                        ? 'border-brand-500 bg-brand-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div>
                      <div className="font-medium text-gray-900">
                        {LANGUAGE_NAMES[variant.language] || variant.language}
                      </div>
                      <div className="text-xs text-gray-500">{variant.language.toUpperCase()}</div>
                    </div>
                    <StatusBadge status={variant.status} />
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Selected variant details */}
          {selectedVariant && (
            <div className="rounded-xl border border-gray-200 bg-white p-4 space-y-3">
              <h3 className="text-sm font-medium text-gray-700">
                {LANGUAGE_NAMES[selectedVariant.language]} Variant Details
              </h3>
              {selectedVariant.title && (
                <div>
                  <span className="text-xs font-medium text-gray-500">Title</span>
                  <p className="text-sm text-gray-800">{selectedVariant.title}</p>
                </div>
              )}
              {selectedVariant.description && (
                <div>
                  <span className="text-xs font-medium text-gray-500">Description</span>
                  <p className="text-sm text-gray-800">{selectedVariant.description}</p>
                </div>
              )}
              {selectedVariant.hashtags && selectedVariant.hashtags.length > 0 && (
                <div>
                  <span className="text-xs font-medium text-gray-500">Hashtags</span>
                  <div className="mt-1 flex flex-wrap gap-1">
                    {selectedVariant.hashtags.map((tag, i) => (
                      <span
                        key={i}
                        className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {selectedVariant.status === 'completed' && (
                <button
                  onClick={() => {
                    setShowPublish(true)
                    setPublishExpanded(true)
                  }}
                  className="mt-2 flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
                >
                  <Send className="h-4 w-4" />
                  Publish This Variant
                </button>
              )}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Details card */}
          <div className="rounded-xl border border-gray-200 bg-white p-5">
            <h3 className="text-sm font-medium text-gray-700">Details</h3>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">Status</dt>
                <dd><StatusBadge status={project.status} /></dd>
              </div>
              {video && (
                <>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Aspect Ratio</dt>
                    <dd className="text-gray-900">{video.aspect_ratio}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-gray-500">Resolution</dt>
                    <dd className="text-gray-900">{video.resolution}</dd>
                  </div>
                  {video.duration_sec && (
                    <div className="flex justify-between">
                      <dt className="text-gray-500">Duration</dt>
                      <dd className="text-gray-900">{Math.round(video.duration_sec)}s</dd>
                    </div>
                  )}
                </>
              )}
              <div className="flex justify-between">
                <dt className="text-gray-500">Created</dt>
                <dd className="text-gray-900">
                  {new Date(project.created_at).toLocaleDateString()}
                </dd>
              </div>
            </dl>
          </div>

          {/* Publish panel */}
          {showPublish && selectedVariant && (
            <div className="rounded-xl border border-brand-200 bg-brand-50 p-5">
              <button
                onClick={() => setPublishExpanded(!publishExpanded)}
                className="flex w-full items-center justify-between text-sm font-medium text-brand-700"
              >
                <span>
                  <Send className="mr-1.5 inline h-4 w-4" />
                  Publish: {LANGUAGE_NAMES[selectedVariant.language]}
                </span>
                {publishExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>

              {publishExpanded && (
                <div className="mt-3 space-y-3">
                  <p className="text-xs text-brand-600">Select platforms to publish to:</p>

                  {activeAccounts.length === 0 ? (
                    <p className="text-xs text-gray-500">
                      No connected accounts.{' '}
                      <span
                        className="cursor-pointer text-brand-600 underline"
                        onClick={() => navigate('/accounts')}
                      >
                        Connect one
                      </span>
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {activeAccounts.map((account) => (
                        <label
                          key={account.id}
                          className={`flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition-colors ${
                            selectedAccounts.includes(account.id)
                              ? 'border-brand-500 bg-white'
                              : 'border-gray-200 bg-white hover:border-gray-300'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={selectedAccounts.includes(account.id)}
                            onChange={() => toggleAccount(account.id)}
                            className="rounded border-gray-300 text-brand-600 focus:ring-brand-500"
                          />
                          <div
                            className={`h-6 w-6 rounded ${PLATFORM_COLORS[account.platform] || 'bg-gray-500'} flex items-center justify-center`}
                          >
                            <span className="text-[10px] font-bold text-white">
                              {account.platform[0].toUpperCase()}
                            </span>
                          </div>
                          <div className="flex-1 text-sm">
                            <div className="font-medium text-gray-900 capitalize">
                              {account.platform}
                            </div>
                            <div className="text-xs text-gray-500">
                              {account.display_name || 'Connected'}
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={handlePublish}
                    disabled={selectedAccounts.length === 0 || publishMutation.isPending}
                    className="w-full rounded-lg bg-brand-600 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
                  >
                    {publishMutation.isPending ? (
                      <><Loader2 className="mr-1.5 inline h-4 w-4 animate-spin" />Publishing...</>
                    ) : (
                      `Publish to ${selectedAccounts.length} platform${selectedAccounts.length !== 1 ? 's' : ''}`
                    )}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Publish Jobs */}
          {relatedJobs.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="text-sm font-medium text-gray-700">Publish History</h3>
              <div className="mt-3 space-y-2">
                {relatedJobs.map((job) => (
                  <div
                    key={job.id}
                    className="flex items-center justify-between rounded-lg bg-gray-50 px-3 py-2 text-sm"
                  >
                    <div className="flex items-center gap-2">
                      {getJobStatusIcon(job.status)}
                      <span className="capitalize text-gray-700">{job.platform}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {job.platform_url && (
                        <a
                          href={job.platform_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-brand-500 hover:text-brand-600"
                        >
                          <ExternalLink className="h-3.5 w-3.5" />
                        </a>
                      )}
                      {job.status === 'failed' && (
                        <button
                          onClick={() => retryMutation.mutate(job.id)}
                          className="text-gray-400 hover:text-brand-500"
                          title="Retry"
                        >
                          <RefreshCw className="h-3.5 w-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Quick publish for all completed variants */}
          {completedVariants.length > 1 && activeAccounts.length > 0 && (
            <div className="rounded-xl border border-gray-200 bg-white p-5">
              <h3 className="text-sm font-medium text-gray-700">Bulk Publish</h3>
              <p className="mt-1 text-xs text-gray-500">
                Publish all {completedVariants.length} language variants at once
              </p>
              <button
                onClick={() => {
                  if (!selectedVariant && completedVariants.length > 0) {
                    setSelectedVariant(completedVariants[0])
                  }
                  setShowPublish(true)
                  setPublishExpanded(true)
                }}
                className="mt-3 w-full rounded-lg border border-brand-200 bg-brand-50 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100"
              >
                <Send className="mr-1.5 inline h-4 w-4" />
                Publish All Variants
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
