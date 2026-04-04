import { Layout } from '@/components/layout'
import { ThemeToggle } from '@/components/theme-toggle'

export function LayoutWithTheme({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <h1 className="text-xl font-bold">Cinder Dashboard</h1>
          <ThemeToggle />
        </div>
      </header>
      <Layout>{children}</Layout>
    </div>
  )
}
