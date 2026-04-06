'use client'

import { useState } from 'react'

interface FeedbackFormProps {
  executionId: number
  estimatedTime?: number
  actualTime?: number
  onSubmit?: () => void
  onCancel?: () => void
}

export default function FeedbackForm({
  executionId,
  estimatedTime,
  actualTime,
  onSubmit,
  onCancel,
}: FeedbackFormProps) {
  const [feedbackType, setFeedbackType] = useState('estimation_accuracy')
  const [rating, setRating] = useState(3)
  const [comment, setComment] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const feedbackTypes = [
    { value: 'estimation_accuracy', label: '预估准确性' },
    { value: 'progress_display', label: '进度展示' },
    { value: 'performance', label: '性能表现' },
    { value: 'bug_report', label: '问题报告' },
    { value: 'feature_request', label: '功能建议' },
    { value: 'general', label: '其他反馈' },
  ]

  const ratingLabels = [
    '非常差',
    '较差',
    '一般',
    '良好',
    '非常好',
  ]

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          execution_id: executionId,
          feedback_type: feedbackType,
          rating,
          comment: comment || null,
          estimated_time: estimatedTime,
          actual_time: actualTime,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to submit feedback')
      }

      if (onSubmit) {
        onSubmit()
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="bg-card border rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">提交反馈</h3>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">反馈类型</label>
          <select
            value={feedbackType}
            onChange={(e) => setFeedbackType(e.target.value)}
            className="w-full border rounded-md px-3 py-2 bg-background"
          >
            {feedbackTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">评分</label>
          <div className="flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setRating(value)}
                className={`w-10 h-10 rounded-full border-2 transition-colors ${
                  rating >= value
                    ? 'bg-primary border-primary text-primary-foreground'
                    : 'border-muted hover:border-primary'
                }`}
              >
                {value}
              </button>
            ))}
            <span className="ml-2 text-sm text-muted-foreground">
              {ratingLabels[rating - 1]}
            </span>
          </div>
        </div>

        {feedbackType === 'estimation_accuracy' && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">预估时间:</span>
              <span>{estimatedTime ? `${estimatedTime.toFixed(1)}秒` : 'N/A'}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">实际时间:</span>
              <span>{actualTime ? `${actualTime.toFixed(1)}秒` : 'N/A'}</span>
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium mb-2">详细反馈（可选）</label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="请分享您的想法和建议..."
            className="w-full border rounded-md px-3 py-2 bg-background min-h-[100px]"
          />
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-md p-3 text-red-500 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-primary text-primary-foreground px-4 py-2 rounded-md hover:opacity-90 disabled:opacity-50"
          >
            {submitting ? '提交中...' : '提交反馈'}
          </button>
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 border rounded-md hover:bg-muted"
            >
              取消
            </button>
          )}
        </div>
      </form>
    </div>
  )
}
