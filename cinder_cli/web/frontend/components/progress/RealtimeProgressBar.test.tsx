import { render, screen, waitFor } from '@testing-library/react'
import RealtimeProgressBar from '@/components/progress/RealtimeProgressBar'

describe('RealtimeProgressBar', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  it('renders without crashing when executionId is null', () => {
    render(<RealtimeProgressBar executionId={null} />)
    expect(screen.getByText(/Phase:/)).toBeInTheDocument()
  })

  it('displays initial progress state', () => {
    render(<RealtimeProgressBar executionId={null} />)
    
    expect(screen.getByText('Phase: idle')).toBeInTheDocument()
    expect(screen.getByText('0.0%')).toBeInTheDocument()
    expect(screen.getByText(/tasks\/min/)).toBeInTheDocument()
  })

  it('shows progress bar with correct width', () => {
    render(<RealtimeProgressBar executionId={null} />)
    
    const progressBar = document.querySelector('.bg-primary')
    expect(progressBar).toHaveStyle({ width: '0%' })
  })

  it('calls onComplete callback when execution finishes', async () => {
    const mockOnComplete = jest.fn()
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    render(<RealtimeProgressBar executionId={1} onComplete={mockOnComplete} />)

    mockEventSource.onopen?.({} as Event)
    
    mockEventSource.onmessage?.({
      data: JSON.stringify({
        status: 'success',
        progress_data: { overall_progress: 100 },
        speed_metrics: { tasks_per_minute: 10 },
      }),
    } as MessageEvent)

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalled()
      expect(mockEventSource.close).toHaveBeenCalled()
    })
  })

  it('updates progress when receiving SSE messages', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    render(<RealtimeProgressBar executionId={1} />)

    mockEventSource.onopen?.({} as Event)
    
    mockEventSource.onmessage?.({
      data: JSON.stringify({
        status: 'running',
        progress_data: { overall_progress: 50 },
        speed_metrics: { tasks_per_minute: 5 },
      }),
    } as MessageEvent)

    await waitFor(() => {
      expect(screen.getByText('50.0%')).toBeInTheDocument()
      expect(screen.getByText('5.0 tasks/min')).toBeInTheDocument()
    })
  })

  it('handles SSE connection errors', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    render(<RealtimeProgressBar executionId={1} />)

    mockEventSource.onerror?.({} as Event)

    await waitFor(() => {
      expect(mockEventSource.close).toHaveBeenCalled()
    })
  })

  it('closes EventSource on unmount', () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const { unmount } = render(<RealtimeProgressBar executionId={1} />)
    
    unmount()

    expect(mockEventSource.close).toHaveBeenCalled()
  })
})
