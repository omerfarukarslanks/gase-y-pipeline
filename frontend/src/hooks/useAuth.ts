import { useMutation } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { authApi } from '../api/auth'
import { useAuthStore } from '../stores/authStore'

export function useLogin() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()

  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    onSuccess: async (response) => {
      setTokens(response.data.access_token, response.data.refresh_token)
      const me = await authApi.getMe()
      setUser(me.data)
      toast.success('Login successful')
      navigate('/')
    },
    onError: () => {
      toast.error('Invalid email or password')
    },
  })
}

export function useRegister() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()

  return useMutation({
    mutationFn: (data: { email: string; password: string; fullName?: string }) =>
      authApi.register(data.email, data.password, data.fullName),
    onSuccess: async (response) => {
      setTokens(response.data.access_token, response.data.refresh_token)
      const me = await authApi.getMe()
      setUser(me.data)
      toast.success('Account created successfully')
      navigate('/')
    },
    onError: () => {
      toast.error('Registration failed')
    },
  })
}

export function useLogout() {
  const navigate = useNavigate()
  const logout = useAuthStore((s) => s.logout)

  return () => {
    logout()
    navigate('/login')
  }
}
