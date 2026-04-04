'use client'

import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import { notFound } from 'next/navigation'
import { apiFetch } from '@/lib/api'

async function fetchExecution(id: string) {
  try {
    return await apiFetch(`/api/executions/${id}`)
  } catch {
    return null
  }
}

export default function ExecutionDetailPage({ params }: { params: { id: string } }) {
  const { data: execution, isLoading } = useQuery({
    queryKey: ['execution', params.id],
    queryFn: () => fetchExecution(params.id),
  })

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-8">加载中...</div>
      </Layout>
    )
  }

  if (!execution) {
    notFound()
  }

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-6">执行详情 #{execution.id}</h2>

      <div className="grid gap-6">
        <div className="bg-card border rounded-lg p-6">
          <h3 className="text-lg font-semibold mb-4">基本信息</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-muted-foreground">目标</dt>
              <dd>{execution.goal}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">状态</dt>
              <dd>
                <span className={`text-sm px-2 py-1 rounded ${
                  execution.status === 'success'
                    ? 'bg-green-500/10 text-green-500'
                    : 'bg-red-500/10 text-red-500'
                }`}>
                  {execution.status}
                </span>
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-muted-foreground">时间</dt>
              <dd>{new Date(execution.timestamp).toLocaleString('zh-CN')}</dd>
            </div>
          </dl>
        </div>

        {execution.created_files?.length > 0 && (
          <div className="bg-card border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">创建的文件</h3>
            <ul className="space-y-2">
              {execution.created_files.map((file: string, index: number) => (
                <li key={index} className="text-muted-foreground">{file}</li>
              ))}
            </ul>
          </div>
        )}

        {execution.task_tree?.subtasks && (
          <div className="bg-card border rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-4">任务树</h3>
            <ul className="space-y-2">
              {execution.task_tree.subtasks.map((task: any, index: number) => (
                <li key={index} className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary/10 text-primary flex items-center justify-center text-sm">
                    {task.id}
                  </span>
                  <span>{task.description}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </Layout>
  )
}
