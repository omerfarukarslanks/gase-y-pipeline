import { useEffect, useRef, useCallback } from 'react'
import { useAuthStore } from '../stores/authStore'

interface JobStatusMessage {
  job_id: string
  status: string
  step?: string
  progress?: number
}

export function useWebSocket(onMessage: (msg: JobStatusMessage) => void) {
  const wsRef = useRef<WebSocket | null>(null)
  const user = useAuthStore((s) => s.user)

  const connect = useCallback(() => {
    if (!user?.id) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/jobs/${user.id}`)

    ws.onmessage = (event) => {
      const data: JobStatusMessage = JSON.parse(event.data)
      onMessage(data)
    }

    ws.onclose = () => {
      // Reconnect after 3 seconds
      setTimeout(connect, 3000)
    }

    wsRef.current = ws
  }, [user?.id, onMessage])

  useEffect(() => {
    connect()
    return () => {
      wsRef.current?.close()
    }
  }, [connect])

  return wsRef
}
