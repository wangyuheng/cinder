"""
Frontend hook for real-time progress updates.
"""

import { useEffect, useState, useRef } from 'react'

interface ProgressData {
  execution_id?: number
  status: string
  progress_data?: any
  speed_metrics?: any
  timestamp?: number
  error?: string
}

export function useRealtimeProgress(executionId: number | null) {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  useEffect(() => {
    if (!executionId) {
      return
    }

    const connectEventSource = () => {
      const url = `/api/executions/${executionId}/progress`
      const eventSource = new EventSource(url)
      
      eventSource.onopen = () => {
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
      }

      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          setProgress(data)
          
          if (data.error) {
            setError(data.error)
          }
          
          if (data.status === 'success' || data.status === 'error' || data.status === 'failed') {
            eventSource.close()
            setIsConnected(false)
          }
        } catch (e) {
          console.error('Failed to parse progress data:', e)
        }
      }

      eventSource.onerror = () => {
        setIsConnected(false)
        eventSource.close()
        
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.pow(2, reconnectAttempts.current) * 1000
          reconnectAttempts.current++
          
          setTimeout(() => {
            connectEventSource()
          }, delay)
        } else {
          setError('Connection failed after multiple attempts')
        }
      }

      eventSourceRef.current = eventSource
    }

    connectEventSource()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
    }
  }, [executionId])

  return {
    progress,
    isConnected,
    error,
  }
}

export function useCurrentProgress() {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    const eventSource = new EventSource('/api/executions/current/progress')
    
    eventSource.onopen = () => {
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setProgress(data)
      } catch (e) {
        console.error('Failed to parse progress data:', e)
      }
    }

    eventSource.onerror = () => {
      setIsConnected(false)
    }

    eventSourceRef.current = eventSource

    return () => {
      eventSource.close()
    }
  }, [])

  return {
    progress,
    isConnected,
  }
}
