'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { createUser } from '@/lib/api'

export default function ProfilePage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    const trimmedName = name.trim()
    
    if (trimmedName.length < 1 || trimmedName.length > 50) {
      setError('姓名长度需要在 1-50 个字符之间')
      return
    }

    setIsLoading(true)

    try {
      await createUser(trimmedName)
      router.push('/onboarding/questionnaire')
    } catch {
      setError('创建用户失败，请稍后重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-md px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">告诉我们你的名字</h1>
          <p className="text-muted-foreground">我们将用这个名字为你创建个性化体验</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2">
              你的名字
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="请输入你的名字"
              maxLength={50}
              className="w-full bg-background border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={isLoading}
              autoFocus
            />
            <p className="mt-1 text-xs text-muted-foreground text-right">
              {name.length}/50
            </p>
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive text-sm rounded-lg px-4 py-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!name.trim() || isLoading}
            className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity font-medium"
          >
            {isLoading ? '创建中...' : '继续'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>步骤 2/3 · 填写信息</p>
          <div className="flex justify-center gap-2 mt-3">
            <div className="w-8 h-1 bg-primary rounded-full" />
            <div className="w-8 h-1 bg-primary rounded-full" />
            <div className="w-8 h-1 bg-muted rounded-full" />
          </div>
        </div>
      </div>
    </div>
  )
}
