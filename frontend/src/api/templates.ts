import apiClient from './client'
import type { Template } from '../types/video'

export const templatesApi = {
  list: (category?: string) =>
    apiClient.get<Template[]>('/templates', { params: category ? { category } : {} }),

  get: (id: string) =>
    apiClient.get<Template>(`/templates/${id}`),

  create: (data: {
    name: string
    category?: string
    description?: string
    scene_structure: Record<string, unknown>
    default_settings?: Record<string, unknown>
  }) => apiClient.post<Template>('/templates', data),

  update: (id: string, data: {
    name?: string
    category?: string
    description?: string
    scene_structure?: Record<string, unknown>
    default_settings?: Record<string, unknown>
  }) => apiClient.put<Template>(`/templates/${id}`, data),

  duplicate: (id: string) =>
    apiClient.post<Template>(`/templates/${id}/duplicate`),

  delete: (id: string) =>
    apiClient.delete(`/templates/${id}`),

  categories: () =>
    apiClient.get<{ categories: string[] }>('/templates/categories'),
}
