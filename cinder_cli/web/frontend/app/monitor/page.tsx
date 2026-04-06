'use client'

import { useEffect, useState, useRef } from 'react'
import { Layout } from '@/components/layout'
import Link from 'next/link'

interface ExecutionProgress {
  execution_id: number
  goal: string
  status: string
  progress: number
  speed: number
  phase: string
  timestamp: number
  elapsed?: number
  remaining?: number
}

interface ActiveExecutionsData {
  executions: ExecutionProgress[]
  count: number
}

export default function MonitorPage() {
  const [activeExecutions, setActiveExecutions] = useState<ExecutionProgress[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = 5

  useEffect(() => {
    const connectEventSource = () => {
      const eventSource = new EventSource('/api/executions/active/monitor')
      
      eventSource.onopen = () => {
        setIsConnected(true)
        setError(null)
        reconnectAttempts.current = 0
      }

      eventSource.onmessage = (event) => {
        try {
          const data: ActiveExecutionsData = JSON.parse(event.data)
          setActiveExecutions(data.executions || [])
        } catch (e) {
          console.error('Failed to parse active executions data:', e)
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
  }, [])

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">实时监控</h2>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isConnected ? '已连接' : '未连接'}
            </span>
          </div>
        </div>
        <Link
          href="/executions"
          className="text-primary hover:underline"
        >
          查看所有执行
        </Link>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
          <p className="text-red-500">{error}</p>
        </div>
      )}

      {activeExecutions.length === 0 ? (
        <div className="bg-card border rounded-lg p-12 text-center">
          <div className="text-6xl mb-4">📊</div>
          <h3 className="text-xl font-semibold mb-2">暂无正在执行的任务</h3>
          <p className="text-muted-foreground mb-4">
            当前没有正在运行的执行任务
          </p>
          <Link
            href="/tasks"
            className="inline-block bg-primary text-primary-foreground px-6 py-2 rounded-lg hover:opacity-90"
          >
            创建新执行
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
            <span>正在执行:</span>
            <span className="font-semibold text-primary">{activeExecutions.length} 个任务</span>
          </div>

          <div className="grid gap-4">
            {activeExecutions.map((execution) => (
              <ExecutionCard key={execution.execution_id} execution={execution} />
            ))}
          </div>
        </div>
      )}
    </Layout>
  )
}

function ExecutionCard({ execution }: { execution: ExecutionProgress }) {
  const progressColor = 
    execution.progress < 30 ? 'bg-yellow-500' :
    execution.progress < 70 ? 'bg-blue-500' :
    'bg-green-500'

  return (
    <div className="bg-card border rounded-lg p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <Link 
            href={`/executions/${execution.execution_id}`}
            className="text-lg font-semibold hover:underline mb-1 block"
          >
            #{execution.execution_id}: {execution.goal}
          </Link>
          <div className="flex items-center gap-4 text-sm text-muted-foreground">
            <span>阶段: {execution.phase}</span>
            <span>•</span>
            <span>状态: {execution.status}</span>
            <span>•</span>
            <span>🚀 {execution.speed.toFixed(1)} tasks/min</span>
          </div>
        </div>
        <span className={`text-sm px-3 py-1 rounded ${
          execution.status === 'running' ? 'bg-blue-500/10 text-blue-500' :
          execution.status === 'success' ? 'bg-green-500/10 text-green-500' :
          'bg-red-500/10 text-red-500'
        }`}>
          {execution.status}
        </span>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">进度</span>
          <span className="font-medium">{execution.progress.toFixed(1)}%</span>
        </div>
        
        <div className="relative w-full h-3 bg-secondary rounded-full overflow-hidden">
          <div
            className={`absolute h-full ${progressColor} transition-all duration-300 ease-out`}
            style={{ width: `${execution.progress}%` }}
          />
        </div>

        <div className="flex justify-between text-xs text-muted-foreground">
          {execution.elapsed && (
            <span>已用时: {formatDuration(execution.elapsed)}</span>
          )}
          {execution.remaining && (
            <span>预计剩余: {formatDuration(execution.remaining)}</span>
          )}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t flex justify-between items-center text-sm">
        <span className="text-muted-foreground">
          开始时间: {new Date(execution.timestamp).toLocaleString('zh-CN')}
        </span>
        <Link
          href={`/executions/${execution.execution_id}`}
          className="text-primary hover:underline"
        >
          查看详情 →
        </Link>
      </div>
    </div>
  )
}

function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.floor(seconds)}秒`
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${minutes}分${secs}秒`
  } else {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}小时${minutes}分`
  }
}
