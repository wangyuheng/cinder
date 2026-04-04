'use client'

import { useMutation } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import { useState } from 'react'
import { apiFetch } from '@/lib/api'

async function triggerTask(data: { goal: string; mode: string }) {
  return apiFetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
}

export default function TasksPage() {
  const [goal, setGoal] = useState('')
  const [mode, setMode] = useState('dry-run')
  const mutation = useMutation({ mutationFn: triggerTask })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    mutation.mutate({ goal, mode })
  }

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-6">任务触发</h2>

      <div className="bg-card border rounded-lg p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">执行目标</label>
            <textarea
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              placeholder="输入执行目标，例如：创建一个Python脚本"
              className="w-full bg-background border rounded-lg px-4 py-3 min-h-[100px]"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">执行模式</label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { value: 'dry-run', label: '预览模式', desc: '不执行，只预览' },
                { value: 'auto', label: '自动模式', desc: '自动执行' },
                { value: 'interactive', label: '交互模式', desc: '逐步确认' },
              ].map((option) => (
                <label
                  key={option.value}
                  className={`flex flex-col p-4 border rounded-lg cursor-pointer transition-colors ${
                    mode === option.value ? 'border-primary bg-primary/5' : 'hover:bg-muted/50'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <input
                      type="radio"
                      name="mode"
                      value={option.value}
                      checked={mode === option.value}
                      onChange={(e) => setMode(e.target.value)}
                      className="sr-only"
                    />
                    <span className="font-medium">{option.label}</span>
                  </div>
                  <span className="text-sm text-muted-foreground mt-1">{option.desc}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={mutation.isPending || !goal}
            className="bg-primary text-primary-foreground px-6 py-3 rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            {mutation.isPending ? '执行中...' : '开始执行'}
          </button>
        </form>

        {mutation.data && (
          <div className="mt-6 p-4 bg-muted rounded-lg">
            <h4 className="font-medium mb-2">执行结果</h4>
            <pre className="text-sm overflow-auto">
              {JSON.stringify(mutation.data, null, 2)}
            </pre>
          </div>
        )}

        {mutation.isError && (
          <div className="mt-6 p-4 bg-red-500/10 text-red-500 rounded-lg">
            执行失败，请重试
          </div>
        )}
      </div>
    </Layout>
  )
}
