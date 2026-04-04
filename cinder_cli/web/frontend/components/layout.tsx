import Link from 'next/link'
import { Activity, Settings, Brain, History, Zap } from 'lucide-react'

const navItems = [
  { href: '/', label: '仪表盘', icon: Activity },
  { href: '/executions', label: '执行历史', icon: History },
  { href: '/soul', label: 'Soul 配置', icon: Brain },
  { href: '/decisions', label: '决策记录', icon: Settings },
  { href: '/tasks', label: '任务触发', icon: Zap },
]

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold">Cinder Dashboard</h1>
          <nav className="flex gap-6">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </div>
      </header>
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
