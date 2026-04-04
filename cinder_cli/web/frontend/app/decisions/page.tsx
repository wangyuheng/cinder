'use client'

import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import { apiFetch } from '@/lib/api'

async function fetchDecisions() {
  return apiFetch('/api/decisions?limit=50')
}

export default function DecisionsPage() {
  const { data, isLoading } = useQuery({ queryKey: ['decisions'], queryFn: fetchDecisions })

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-6">决策记录</h2>

      {isLoading ? (
        <div className="text-center py-8">加载中...</div>
      ) : (
        <div className="bg-card border rounded-lg">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-4">ID</th>
                <th className="text-left p-4">上下文</th>
                <th className="text-left p-4">置信度</th>
                <th className="text-left p-4">需要人工</th>
                <th className="text-left p-4">时间</th>
              </tr>
            </thead>
            <tbody>
              {data?.decisions?.map((decision: any) => (
                <tr key={decision.id} className="border-b last:border-0 hover:bg-muted/50">
                  <td className="p-4">#{decision.id}</td>
                  <td className="p-4 max-w-md truncate">{decision.context?.description || '-'}</td>
                  <td className="p-4">
                    <span
                      className={`text-sm px-2 py-1 rounded ${
                        decision.confidence >= 0.7
                          ? 'bg-green-500/10 text-green-500'
                          : decision.confidence >= 0.5
                          ? 'bg-yellow-500/10 text-yellow-500'
                          : 'bg-red-500/10 text-red-500'
                      }`}
                    >
                      {(decision.confidence * 100).toFixed(0)}%
                    </span>
                  </td>
                  <td className="p-4">
                    {decision.requires_human ? (
                      <span className="text-yellow-500">是</span>
                    ) : (
                      <span className="text-green-500">否</span>
                    )}
                  </td>
                  <td className="p-4 text-muted-foreground">
                    {decision.timestamp ? new Date(decision.timestamp).toLocaleString('zh-CN') : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {data?.decisions?.length === 0 && (
            <div className="text-center py-8 text-muted-foreground">暂无决策记录</div>
          )}
        </div>
      )}
    </Layout>
  )
}
