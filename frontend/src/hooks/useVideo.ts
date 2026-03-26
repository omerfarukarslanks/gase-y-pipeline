import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { projectsApi } from '../api/projects'
import { videosApi } from '../api/videos'
import { platformsApi } from '../api/platforms'
import type { VideoGenerateRequest } from '../types/video'

export function useProjects(page = 1) {
  return useQuery({
    queryKey: ['projects', page],
    queryFn: () => projectsApi.list(page),
    select: (res) => res.data,
  })
}

export function useProject(id: string) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => projectsApi.get(id),
    select: (res) => res.data,
    enabled: !!id,
  })
}

export function useCreateProject() {
  return useMutation({
    mutationFn: (data: { title: string; prompt: string; settings?: Record<string, unknown> }) =>
      projectsApi.create(data),
    onSuccess: () => toast.success('Project created'),
    onError: () => toast.error('Failed to create project'),
  })
}

export function useGenerateVideo() {
  return useMutation({
    mutationFn: (data: VideoGenerateRequest) => videosApi.generate(data),
    onSuccess: () => toast.success('Video generation started'),
    onError: () => toast.error('Failed to start video generation'),
  })
}

export function useVideoVariants(videoId: string) {
  return useQuery({
    queryKey: ['video-variants', videoId],
    queryFn: () => videosApi.getVariants(videoId),
    select: (res) => res.data,
    enabled: !!videoId,
  })
}

export function usePlatformAccounts() {
  return useQuery({
    queryKey: ['platform-accounts'],
    queryFn: () => platformsApi.list(),
    select: (res) => res.data,
  })
}

export function usePublishJobs(params?: { page?: number; platform?: string; status?: string }) {
  return useQuery({
    queryKey: ['publish-jobs', params],
    queryFn: () => platformsApi.listJobs(params),
    select: (res) => res.data,
  })
}

export function usePublishVideo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: platformsApi.publish,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publish-jobs'] })
      toast.success('Publishing started')
    },
    onError: () => toast.error('Failed to publish'),
  })
}

export function useRetryPublish() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (jobId: string) => platformsApi.retryJob(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['publish-jobs'] })
      toast.success('Retrying publish...')
    },
    onError: () => toast.error('Failed to retry'),
  })
}
