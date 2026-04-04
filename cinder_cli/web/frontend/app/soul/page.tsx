'use client'

import { useQuery, useMutation } from '@tanstack/react-query'
import { Layout } from '@/components/layout'
import { useState } from 'react'
import { apiFetch } from '@/lib/api'

async function fetchSoul() {
  return apiFetch('/api/soul')
}

async function updateSoul(traits: any) {
  return apiFetch('/api/soul', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ traits }),
  })
}

export default function SoulPage() {
  const { data: soul, isLoading } = useQuery({ queryKey: ['soul'], queryFn: fetchSoul })
  const mutation = useMutation({ mutationFn: updateSoul })

  const [traits, setTraits] = useState({
    risk_tolerance: 50,
    structure: 50,
    detail_orientation: 50,
    communication_style: 'balanced',
  })

  if (isLoading) {
    return (
      <Layout>
        <div className="text-center py-8">加载中...</div>
      </Layout>
    )
  }

  const handleSave = () => {
    mutation.mutate(traits)
  }

  return (
    <Layout>
      <h2 className="text-2xl font-bold mb-6">Soul 配置</h2>

      <div className="bg-card border rounded-lg p-6">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">风险容忍度</label>
            <input
              type="range"
              min="0"
              max="100"
              defaultValue={soul?.traits?.risk_tolerance || 50}
              onChange={(e) => setTraits({ ...traits, risk_tolerance: Number(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>保守</span>
              <span>激进</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">结构化程度</label>
            <input
              type="range"
              min="0"
              max="100"
              defaultValue={soul?.traits?.structure || 50}
              onChange={(e) => setTraits({ ...traits, structure: Number(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>灵活</span>
              <span>严谨</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">细节关注度</label>
            <input
              type="range"
              min="0"
              max="100"
              defaultValue={soul?.traits?.detail_orientation || 50}
              onChange={(e) => setTraits({ ...traits, detail_orientation: Number(e.target.value) })}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>宏观</span>
              <span>微观</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">沟通风格</label>
            <select
              defaultValue={soul?.traits?.communication_style || 'balanced'}
              onChange={(e) => setTraits({ ...traits, communication_style: e.target.value })}
              className="w-full bg-background border rounded-lg px-4 py-2"
            >
              <option value="concise">简洁</option>
              <option value="balanced">平衡</option>
              <option value="detailed">详细</option>
            </select>
          </div>

          <button
            onClick={handleSave}
            disabled={mutation.isPending}
            className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50"
          >
            {mutation.isPending ? '保存中...' : '保存配置'}
          </button>

          {mutation.isSuccess && (
            <p className="text-green-500 text-sm">配置已保存</p>
          )}
        </div>
      </div>
    </Layout>
  )
}
