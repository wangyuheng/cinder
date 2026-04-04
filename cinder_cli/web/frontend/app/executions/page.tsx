'use client'

import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import Link from 'next/link'
import { apiFetch } from '@/lib/api'

async function fetchExecutions() {
  return apiFetch('/api/executions?limit=50')
}

export default function ExecutionsPage() {
  const { data, isLoading } = useQuery({ queryKey: ['executions'], queryFn: fetchExecutions })

  return (
    <Layout>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">执行历史</h2>
        <Link
          href="/tasks"
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90"
        >
          新建执行
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="bg-card border rounded-lg">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-4">目标</th>
                <th className="text-left p-4">状态</th>
                <th className="text-left p-4">文件数</th>
                <th className="text-left p-4">时间</th>
              </tr>
            </thead>
            <tbody>
              {data?.executions?.map((execution: any) => (
                <tr key={execution.id} className="border-b last:border-0 hover:bg-muted/50">
                  <td className="p-4">
                    <Link href={`/executions/${execution.id}`} className="hover:underline">
                      {execution.goal}
                    </Link>
                  </td>
                  <td className="p-4">
                    <span
                      className={`text-sm px-2 py-1 rounded ${
                        execution.status === 'success'
                          ? 'bg-green-500/10 text-green-500'
                          : 'bg-red-500/10 text-red-500'
                      }`}
                    >
                      {execution.status}
                    </span>
                  </td>
                  <td className="p-4">{execution.created_files?.length || 0}</td>
                  <td className="p-4 text-muted-foreground">
                    {new Date(execution.timestamp).toLocaleString('zh-CN')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {data?.executions?.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">暂无执行记录</div>
          )}
        </div>
      )}
    </Layout>
  )
}
