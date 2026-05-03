'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { validateInvitation } from '@/lib/api'

export default function InvitationPage() {
  const router = useRouter()
  const [code, setCode] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      const result = await validateInvitation(code)
      
      if (result.valid) {
        router.push('/onboarding/profile')
      } else {
        setError(result.message)
      }
    } catch {
      setError('验证失败，请稍后重试')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-md px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">欢迎使用 Cinder</h1>
          <p className="text-muted-foreground">请输入邀请码以开始使用</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="code" className="block text-sm font-medium mb-2">
              邀请码
            </label>
            <input
              id="code"
              type="text"
              value={code}
              onChange={(e) => setCode(e.target.value)}
              placeholder="请输入邀请码"
              className="w-full bg-background border rounded-lg px-4 py-3 text-center text-lg tracking-widest focus:outline-none focus:ring-2 focus:ring-primary"
              disabled={isLoading}
              autoFocus
            />
          </div>

          {error && (
            <div className="bg-destructive/10 text-destructive text-sm rounded-lg px-4 py-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={!code.trim() || isLoading}
            className="w-full bg-primary text-primary-foreground px-4 py-3 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity font-medium"
          >
            {isLoading ? '验证中...' : '验证邀请码'}
          </button>
        </form>

        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>步骤 1/3 · 邀请码验证</p>
          <div className="flex justify-center gap-2 mt-3">
            <div className="w-8 h-1 bg-primary rounded-full" />
            <div className="w-8 h-1 bg-muted rounded-full" />
            <div className="w-8 h-1 bg-muted rounded-full" />
          </div>
        </div>
      </div>
    </div>
  )
}
