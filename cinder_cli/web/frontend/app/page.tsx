'use client'

import { useQuery } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import { StatsCard } from '@/components/dashboard/stats-card'
import { RecentExecutions } from '@/components/dashboard/recent-executions'
import { Activity, CheckCircle, Brain, FileText } from 'lucide-react'
import { apiFetch } from '@/lib/api'

async function fetchStats() {
  return apiFetch('/api/executions/stats')
}

async function fetchDecisionStats() {
  return apiFetch('/api/decisions/stats')
}

async function fetchExecutions() {
  return apiFetch('/api/executions?limit=5')
}

export default function HomePage() {
  const { data: execStats } = useQuery({ queryKey: ['execStats'], queryFn: fetchStats })
  const { data: decisionStats } = useQuery({ queryKey: ['decisionStats'], queryFn: fetchDecisionStats })
  const { data: executions } = useQuery({ queryKey: ['executions'], queryFn: fetchExecutions })

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-6">仪表盘</h2>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatsCard
          title="执行次数"
          value={execStats?.total || 0}
          icon={Activity}
        />
        <StatsCard
          title="成功率"
          value={execStats?.success_rate ? `${(execStats.success_rate * 100).toFixed(1)}%` : '0%'}
          icon={CheckCircle}
        />
        <StatsCard
          title="决策数"
          value={decisionStats?.total || 0}
          icon={Brain}
        />
        <StatsCard
          title="文件数"
          value={execStats?.total_files || 0}
          icon={FileText}
        />
      </div>

      <RecentExecutions executions={executions?.executions || []} />
    </Layout>
  )
}
