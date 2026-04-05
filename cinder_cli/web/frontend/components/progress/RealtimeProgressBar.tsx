"""
Real-time Progress Bar Component.
"""

'use client'

import { useEffect, useState } from 'react'

interface RealtimeProgressBarProps {
  executionId: number | null
  onComplete?: () => void
}

export default function RealtimeProgressBar({ executionId, onComplete }: RealtimeProgressBarProps) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('idle')
  const [speed, setSpeed] = useState(0)
  const [elapsed, setElapsed] = useState(0)
  const [remaining, setRemaining] = useState<number | null>(null)

  useEffect(() => {
    if (!executionId) return

    const eventSource = new EventSource(`/api/executions/${executionId}/progress`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.progress_data) {
          setProgress(data.progress_data.overall_progress || 0)
          setStatus(data.status || 'unknown')
        }
        
        if (data.speed_metrics) {
          setSpeed(data.speed_metrics.tasks_per_minute || 0)
        }
        
        if (data.status === 'success' || data.status === 'error' || data.status === 'failed') {
          eventSource.close()
          if (onComplete) onComplete()
        }
      } catch (e) {
        console.error('Failed to parse progress data:', e)
      }
    }

    eventSource.onerror = () => {
      console.error('SSE connection error')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [executionId, onComplete])

  return (
    <div className="w-full space-y-2">
      <div className="flex justify-between text-sm text-muted-foreground">
        <span>Phase: {status}</span>
        <span>{progress.toFixed(1)}%</span>
      </div>
      
      <div className="relative w-full h-2 bg-secondary rounded-full overflow-hidden">
        <div
          className="absolute h-full bg-primary transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>🚀 {speed.toFixed(1)} tasks/min</span>
        {remaining !== null && (
          <span>⏱ ~{Math.ceil(remaining / 60)}min remaining</span>
        )}
      </div>
    </div>
  )
}
