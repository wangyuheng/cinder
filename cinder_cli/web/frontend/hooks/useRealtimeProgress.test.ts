import { renderHook, act, waitFor } from '@testing-library/react'
import { useRealtimeProgress, useCurrentProgress } from '@/hooks/useRealtimeProgress'

describe('useRealtimeProgress', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  it('returns initial state when executionId is null', () => {
    const { result } = renderHook(() => useRealtimeProgress(null))

    expect(result.current.progress).toBeNull()
    expect(result.current.isConnected).toBe(false)
    expect(result.current.connectionMode).toBe('sse')
  })

  it('establishes SSE connection when executionId is provided', () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    renderHook(() => useRealtimeProgress(1))

    expect(global.EventSource).toHaveBeenCalledWith('/api/executions/1/progress')
  })

  it('updates progress when receiving SSE messages', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const { result } = renderHook(() => useRealtimeProgress(1))

    act(() => {
      mockEventSource.onopen?.({} as Event)
    })

    expect(result.current.isConnected).toBe(true)
    expect(result.current.connectionMode).toBe('sse')

    act(() => {
      mockEventSource.onmessage?.({
        data: JSON.stringify({
          execution_id: 1,
          status: 'running',
          progress_data: { overall_progress: 50 },
          speed_metrics: { tasks_per_minute: 10 },
        }),
      } as MessageEvent)
    })

    await waitFor(() => {
      expect(result.current.progress).toEqual({
        execution_id: 1,
        status: 'running',
        progress_data: { overall_progress: 50 },
        speed_metrics: { tasks_per_minute: 10 },
      })
    })
  })

  it('closes connection when execution completes', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const { result } = renderHook(() => useRealtimeProgress(1))

    act(() => {
      mockEventSource.onopen?.({} as Event)
    })

    act(() => {
      mockEventSource.onmessage?.({
        data: JSON.stringify({
          status: 'success',
        }),
      } as MessageEvent)
    })

    await waitFor(() => {
      expect(mockEventSource.close).toHaveBeenCalled()
      expect(result.current.isConnected).toBe(false)
    })
  })

  it('falls back to polling after SSE connection failures', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const mockFetch = jest.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          status: 'running',
          progress_data: { overall_progress: 30 },
        }),
      })
    ;(global as any).fetch = mockFetch

    const { result } = renderHook(() => useRealtimeProgress(1))

    act(() => {
      for (let i = 0; i < 6; i++) {
        mockEventSource.onerror?.({} as Event)
      }
    })

    await waitFor(() => {
      expect(result.current.connectionMode).toBe('polling')
    })
  })

  it('cleans up EventSource on unmount', () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const { unmount } = renderHook(() => useRealtimeProgress(1))

    unmount()

    expect(mockEventSource.close).toHaveBeenCalled()
  })
})

describe('useCurrentProgress', () => {
  beforeEach(() => {
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
    jest.clearAllMocks()
  })

  it('establishes SSE connection for current progress', () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    renderHook(() => useCurrentProgress())

    expect(global.EventSource).toHaveBeenCalledWith('/api/executions/current/progress')
  })

  it('updates progress when receiving messages', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const { result } = renderHook(() => useCurrentProgress())

    act(() => {
      mockEventSource.onopen?.({} as Event)
    })

    expect(result.current.isConnected).toBe(true)

    act(() => {
      mockEventSource.onmessage?.({
        data: JSON.stringify({
          status: 'active',
          message: 'Progress streaming active',
        }),
      } as MessageEvent)
    })

    await waitFor(() => {
      expect(result.current.progress).toEqual({
        status: 'active',
        message: 'Progress streaming active',
      })
    })
  })

  it('falls back to polling after SSE failures', async () => {
    const mockEventSource = {
      close: jest.fn(),
      onmessage: null,
      onerror: null,
      onopen: null,
    }

    ;(global as any).EventSource = jest.fn(() => mockEventSource)

    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ status: 'active' }),
    })
    ;(global as any).fetch = mockFetch

    const { result } = renderHook(() => useCurrentProgress())

    act(() => {
      for (let i = 0; i < 6; i++) {
        mockEventSource.onerror?.({} as Event)
      }
    })

    await waitFor(() => {
      expect(result.current.connectionMode).toBe('polling')
    })
  })
})
