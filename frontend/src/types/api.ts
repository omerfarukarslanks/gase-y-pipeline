export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface PaginatedResponse<T> {
  total: number
  page: number
  per_page: number
  pages: number
  items: T[]
}

export interface MessageResponse {
  message: string
}
