'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { getQuestionnaire, submitAnswer, completeQuestionnaire, getQuestionnaireProgress } from '@/lib/api'

interface QuestionOption {
  key: string
  text: string
  summary: string
}

interface Question {
  key: string
  title: string
  prompt: string
  dimension: string
  options: QuestionOption[]
}

export default function QuestionnairePage() {
  const router = useRouter()
  const [questions, setQuestions] = useState<Question[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, { choice: string; reason: string }>>({})
  const [reason, setReason] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [userId, setUserId] = useState<number>(1)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [questionData, progressData] = await Promise.all([
        getQuestionnaire(),
        getQuestionnaireProgress(userId).catch(() => null),
      ])
      
      setQuestions(questionData)
      
      if (progressData?.answers) {
        setAnswers(progressData.answers)
        const completedCount = Object.keys(progressData.answers).length
        if (completedCount > 0 && completedCount < questionData.length) {
          setCurrentIndex(completedCount)
        }
      }
    } catch {
      setError('加载问卷失败')
    } finally {
      setIsLoading(false)
    }
  }

  const currentQuestion = questions[currentIndex]
  const currentAnswer = currentQuestion ? answers[currentQuestion.key] : null
  const isLastQuestion = currentIndex === questions.length - 1
  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0

  useEffect(() => {
    if (currentAnswer) {
      setReason(currentAnswer.reason || '')
    } else {
      setReason('')
    }
  }, [currentIndex, currentAnswer])

  const handleSelectOption = (optionKey: string) => {
    if (!currentQuestion) return
    
    setAnswers(prev => ({
      ...prev,
      [currentQuestion.key]: {
        choice: optionKey,
        reason: prev[currentQuestion.key]?.reason || '',
      },
    }))
  }

  const handleNext = async () => {
    if (!currentQuestion || !answers[currentQuestion.key]) return

    setIsSubmitting(true)
    setError('')

    try {
      const answer = answers[currentQuestion.key]
      await submitAnswer(userId, currentQuestion.key, answer.choice, answer.reason || '')

      if (isLastQuestion) {
        await completeQuestionnaire(userId)
        router.push('/')
      } else {
        setCurrentIndex(prev => prev + 1)
      }
    } catch {
      setError('保存答案失败，请重试')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handlePrev = () => {
    if (currentIndex > 0) {
      setCurrentIndex(prev => prev - 1)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">加载问卷中...</p>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-muted-foreground">暂无问卷</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="w-full max-w-2xl px-4">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm text-muted-foreground">
              问题 {currentIndex + 1}/{questions.length}
            </span>
            <span className="text-sm text-muted-foreground">
              {currentQuestion?.dimension}
            </span>
          </div>
          <div className="w-full bg-muted rounded-full h-2">
            <div
              className="bg-primary rounded-full h-2 transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="mb-8">
          <h2 className="text-xl font-bold mb-3">{currentQuestion?.title}</h2>
          <p className="text-muted-foreground">{currentQuestion?.prompt}</p>
        </div>

        <div className="space-y-3 mb-6">
          {currentQuestion?.options.map((option) => (
            <button
              key={option.key}
              onClick={() => handleSelectOption(option.key)}
              className={`w-full text-left p-4 rounded-lg border transition-all ${
                answers[currentQuestion.key]?.choice === option.key
                  ? 'border-primary bg-primary/5 ring-2 ring-primary/20'
                  : 'border-border hover:border-primary/50'
              }`}
            >
              <div className="flex items-start gap-3">
                <span className={`flex-shrink-0 w-7 h-7 rounded-full border-2 flex items-center justify-center text-sm font-medium ${
                  answers[currentQuestion.key]?.choice === option.key
                    ? 'border-primary bg-primary text-primary-foreground'
                    : 'border-muted-foreground'
                }`}>
                  {option.key}
                </span>
                <div>
                  <p className="font-medium">{option.text}</p>
                  <p className="text-sm text-muted-foreground mt-1">{option.summary}</p>
                </div>
              </div>
            </button>
          ))}
        </div>

        {answers[currentQuestion.key]?.choice && (
          <div className="mb-6">
            <label htmlFor="reason" className="block text-sm font-medium mb-2 text-muted-foreground">
              可选：用一句话补充原因
            </label>
            <input
              id="reason"
              type="text"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value)
                if (currentQuestion) {
                  setAnswers(prev => ({
                    ...prev,
                    [currentQuestion.key]: {
                      ...prev[currentQuestion.key],
                      reason: e.target.value,
                    },
                  }))
                }
              }}
              placeholder="直接回车可跳过"
              className="w-full bg-background border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        )}

        {error && (
          <div className="bg-destructive/10 text-destructive text-sm rounded-lg px-4 py-3 mb-4">
            {error}
          </div>
        )}

        <div className="flex justify-between">
          <button
            onClick={handlePrev}
            disabled={currentIndex === 0}
            className="px-6 py-2 rounded-lg border hover:bg-accent disabled:opacity-50 transition-opacity"
          >
            上一步
          </button>
          <button
            onClick={handleNext}
            disabled={!answers[currentQuestion.key]?.choice || isSubmitting}
            className="bg-primary text-primary-foreground px-6 py-2 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity font-medium"
          >
            {isSubmitting ? '保存中...' : isLastQuestion ? '完成问卷' : '下一步'}
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>步骤 3/3 · SOUL 问卷</p>
          <div className="flex justify-center gap-2 mt-3">
            <div className="w-8 h-1 bg-primary rounded-full" />
            <div className="w-8 h-1 bg-primary rounded-full" />
            <div className="w-8 h-1 bg-primary rounded-full" />
          </div>
        </div>
      </div>
    </div>
  )
}
