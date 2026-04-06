"""
Frontend hook for real-time progress updates with SSE and polling fallback.
"""

import { useEffect, useState, useRef, useCallback } from 'react'

interface ProgressData {
  execution_id?: number
  status: string
  progress_data?: any
  speed_metrics?: any
  timestamp?: number
  error?: string
}

type ConnectionMode = 'sse' | 'polling'

export function useRealtimeProgress(executionId: number | null) {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [connectionMode, setConnectionMode] = useState<ConnectionMode>('sse')
  const eventSourceRef = useRef<EventSource | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const pollingInterval = 2000

  const fetchProgress = useCallback(async () => {
    if (!executionId) return
    
    try {
      const response = await fetch(`/api/executions/${executionId}`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setProgress({
        execution_id: data.id,
        status: data.status,
        progress_data: data.progress_data,
        speed_metrics: data.speed_metrics,
        timestamp: data.timestamp,
      })
      
      if (data.status === 'success' || data.status === 'error' || data.status === 'failed') {
        if (pollingIntervalRef.current) {
          clearInterval(pollingIntervalRef.current)
        }
        setIsConnected(false)
      }
    } catch (e) {
      console.error('Failed to fetch progress data:', e)
      setError('Failed to fetch progress data')
    }
  }, [executionId])

  const startPolling = useCallback(() => {
    setConnectionMode('polling')
    setIsConnected(true)
    setError(null)
    
    fetchProgress()
    
    pollingIntervalRef.current = setInterval(fetchProgress, pollingInterval)
  }, [fetchProgress])

  const connectEventSource = useCallback(() => {
    if (!executionId) return
    
    const url = `/api/executions/${executionId}/progress`
    const eventSource = new EventSource(url)
    
    eventSource.onopen = () => {
      setIsConnected(true)
      setError(null)
      setConnectionMode('sse')
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
        console.log('SSE connection failed, falling back to polling')
        startPolling()
      }
    }

    eventSourceRef.current = eventSource
  }, [executionId, startPolling])

  useEffect(() => {
    if (!executionId) {
      return
    }

    connectEventSource()

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close()
      }
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [executionId, connectEventSource])

  return {
    progress,
    isConnected,
    error,
    connectionMode,
  }
}

export function useCurrentProgress() {
  const [progress, setProgress] = useState<ProgressData | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [connectionMode, setConnectionMode] = useState<ConnectionMode>('sse')
  const eventSourceRef = useRef<EventSource | null>(null)
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5
  const pollingInterval = 2000

  const fetchCurrentProgress = useCallback(async () => {
    try {
      const response = await fetch('/api/executions/current/progress')
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      setProgress(data)
    } catch (e) {
      console.error('Failed to fetch current progress:', e)
    }
  }, [])

  const startPolling = useCallback(() => {
    setConnectionMode('polling')
    setIsConnected(true)
    
    fetchCurrentProgress()
    
    pollingIntervalRef.current = setInterval(fetchCurrentProgress, pollingInterval)
  }, [fetchCurrentProgress])

  useEffect(() => {
    const eventSource = new EventSource('/api/executions/current/progress')
    
    eventSource.onopen = () => {
      setIsConnected(true)
      setConnectionMode('sse')
      reconnectAttempts.current = 0
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
      eventSource.close()
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        const delay = Math.pow(2, reconnectAttempts.current) * 1000
        reconnectAttempts.current++
        
        setTimeout(() => {
          const newEventSource = new EventSource('/api/executions/current/progress')
          eventSourceRef.current = newEventSource
        }, delay)
      } else {
        console.log('SSE connection failed, falling back to polling')
        startPolling()
      }
    }

    eventSourceRef.current = eventSource

    return () => {
      eventSource.close()
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current)
      }
    }
  }, [startPolling])

  return {
    progress,
    isConnected,
    connectionMode,
  }
}
