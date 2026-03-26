import apiClient from './client'
import type { TokenResponse } from '../types/api'

export const authApi = {
  register: (email: string, password: string, fullName?: string) =>
    apiClient.post<TokenResponse>('/auth/register', {
      email,
      password,
      full_name: fullName,
    }),

  login: (email: string, password: string) =>
    apiClient.post<TokenResponse>('/auth/login', { email, password }),

  getMe: () => apiClient.get('/auth/me'),

  updateMe: (data: { full_name?: string; preferences?: Record<string, unknown> }) =>
    apiClient.put('/auth/me', data),
}
