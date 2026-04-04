interface Execution {
  id: number
  goal: string
  status: string
  timestamp: string
  created_files?: string[]
}

interface RecentExecutionsProps {
  executions: Execution[]
}

export function RecentExecutions({ executions }: RecentExecutionsProps) {
  if (executions.length === 0) {
    return (
      <div className="bg-card border rounded-lg p-6">
        <h3 className="text-lg font-semibold mb-4">最近执行</h3>
        <p className="text-muted-foreground">暂无执行记录</p>
      </div>
    )
  }

  return (
    <div className="bg-card border rounded-lg p-6">
      <h3 className="text-lg font-semibold mb-4">最近执行</h3>
      <div className="space-y-4">
        {executions.map((execution) => (
          <div
            key={execution.id}
            className="flex items-center justify-between py-3 border-b last:border-0"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-2 h-2 rounded-full ${
                  execution.status === 'success' ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
              <div>
                <p className="font-medium">{execution.goal}</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(execution.timestamp).toLocaleString('zh-CN')}
                </p>
              </div>
            </div>
            <span
              className={`text-sm px-2 py-1 rounded ${
                execution.status === 'success'
                  ? 'bg-green-500/10 text-green-500'
                  : 'bg-red-500/10 text-red-500'
              }`}
            >
              {execution.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
