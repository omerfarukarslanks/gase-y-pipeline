import apiClient from './client'
import type { Project } from '../types/video'

export const projectsApi = {
  list: (page = 1, perPage = 20) =>
    apiClient.get<Project[]>('/projects', { params: { page, per_page: perPage } }),

  get: (id: string) => apiClient.get<Project>(`/projects/${id}`),

  create: (data: { title: string; prompt: string; settings?: Record<string, unknown> }) =>
    apiClient.post<Project>('/projects', data),

  update: (id: string, data: { title?: string; settings?: Record<string, unknown> }) =>
    apiClient.put<Project>(`/projects/${id}`, data),

  delete: (id: string) => apiClient.delete(`/projects/${id}`),
}
