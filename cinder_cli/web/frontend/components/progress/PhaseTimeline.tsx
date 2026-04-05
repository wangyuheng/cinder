"""
Phase Timeline Component.
"""

'use client'

interface Phase {
  name: string
  status: 'pending' | 'active' | 'completed' | 'error'
  duration?: number
  progress?: number
}

interface PhaseTimelineProps {
  phases: Phase[]
}

export default function PhaseTimeline({ phases }: PhaseTimelineProps) {
  const getStatusIcon = (status: Phase['status']) => {
    switch (status) {
      case 'completed':
        return '✓'
      case 'active':
        return '⏳'
      case 'error':
        return '✗'
      default:
        return '⏸'
    }
  }

  const getStatusColor = (status: Phase['status']) => {
    switch (status) {
      case 'completed':
        return 'text-green-500'
      case 'active':
        return 'text-blue-500 animate-pulse'
      case 'error':
        return 'text-red-500'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="space-y-3">
      {phases.map((phase, index) => (
        <div key={phase.name} className="flex items-start gap-3">
          <div className="flex flex-col items-center">
            <div className={`text-lg ${getStatusColor(phase.status)}`}>
              {getStatusIcon(phase.status)}
            </div>
            {index < phases.length - 1 && (
              <div className="w-0.5 h-8 bg-border mt-1" />
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between">
              <h4 className="text-sm font-medium capitalize">
                {phase.name}
              </h4>
              {phase.duration !== undefined && (
                <span className="text-xs text-muted-foreground">
                  {phase.duration.toFixed(1)}s
                </span>
              )}
            </div>
            
            {phase.status === 'active' && phase.progress !== undefined && (
              <div className="mt-2">
                <div className="w-full h-1 bg-secondary rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${phase.progress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
