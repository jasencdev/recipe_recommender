import React, { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'

type ToastType = 'success' | 'error' | 'info' | 'warning'

type ToastItem = {
  id: number
  type: ToastType
  title?: string
  message: string
  duration: number
}

type AddToastInput = {
  type?: ToastType
  title?: string
  message: string
  duration?: number
}

type ToastContextValue = {
  addToast: (input: AddToastInput) => void
  success: (message: string, title?: string, duration?: number) => void
  error: (message: string, title?: string, duration?: number) => void
  info: (message: string, title?: string, duration?: number) => void
  warning: (message: string, title?: string, duration?: number) => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([])
  const idRef = useRef(0)

  const remove = useCallback((id: number) => {
    setToasts((t) => t.filter((toast) => toast.id !== id))
  }, [])

  const addToast = useCallback((input: AddToastInput) => {
    const id = ++idRef.current
    const duration = input.duration ?? 3500
    const item: ToastItem = {
      id,
      type: input.type ?? 'info',
      title: input.title,
      message: input.message,
      duration,
    }
    setToasts((t) => [...t, item])

    // Auto-remove
    window.setTimeout(() => remove(id), duration)
  }, [remove])

  const api = useMemo<ToastContextValue>(() => ({
    addToast,
    success: (message, title = 'Success', duration) => addToast({ type: 'success', title, message, duration }),
    error: (message, title = 'Error', duration) => addToast({ type: 'error', title, message, duration }),
    info: (message, title = 'Info', duration) => addToast({ type: 'info', title, message, duration }),
    warning: (message, title = 'Warning', duration) => addToast({ type: 'warning', title, message, duration }),
  }), [addToast])

  return (
    <ToastContext.Provider value={api}>
      {children}
      <ToastViewport toasts={toasts} onClose={remove} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) {
    // Fallback no-op API to avoid hard dependency in tests or isolated renders
    const noop = () => {}
    return {
      addToast: noop,
      success: noop,
      error: noop,
      info: noop,
      warning: noop,
    }
  }
  return ctx
}

function ToastViewport({ toasts, onClose }: { toasts: ToastItem[]; onClose: (id: number) => void }) {
  return (
    <div className="fixed top-4 right-4 z-50 flex w-full max-w-sm flex-col gap-2">
      {toasts.map((t) => (
        <Toast key={t.id} toast={t} onClose={() => onClose(t.id)} />
      ))}
    </div>
  )
}

function Toast({ toast, onClose }: { toast: ToastItem; onClose: () => void }) {
  const colors: Record<ToastType, string> = {
    success: 'bg-green-50 text-green-800 border-green-200 dark:bg-green-900/30 dark:text-green-100 dark:border-green-800',
    error: 'bg-red-50 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-100 dark:border-red-800',
    info: 'bg-blue-50 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-100 dark:border-blue-800',
    warning: 'bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-900/30 dark:text-amber-100 dark:border-amber-800',
  }

  const icons: Record<ToastType, React.ReactNode> = {
    success: (
      <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-7.364 7.364a1 1 0 01-1.414 0L3.293 9.829a1 1 0 111.414-1.414l3.222 3.222 6.657-6.657a1 1 0 011.414 0z" clipRule="evenodd" />
      </svg>
    ),
    error: (
      <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm-1-5a1 1 0 112 0 1 1 0 01-2 0zm.293-7.707a1 1 0 011.414 0l.293.293V10a1 1 0 11-2 0V5.586l.293-.293z" clipRule="evenodd" />
      </svg>
    ),
    info: (
      <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
        <path d="M18 10A8 8 0 11.001 10 8 8 0 0118 10zM9 9h2v6H9V9zm2-4H9v2h2V5z" />
      </svg>
    ),
    warning: (
      <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.72-1.36 3.485 0l6.514 11.583c.75 1.334-.213 3.018-1.742 3.018H3.485c-1.53 0-2.492-1.684-1.743-3.018L8.257 3.1zM11 14a1 1 0 10-2 0 1 1 0 002 0zm-1-2a1 1 0 01-1-1V8a1 1 0 112 0v3a1 1 0 01-1 1z" clipRule="evenodd" />
      </svg>
    ),
  }

  return (
    <div
      className={`flex items-start gap-3 rounded-lg border p-3 shadow-md ring-1 ring-black/5 transition-all ${colors[toast.type]}`}
      role="status"
      aria-live="polite"
    >
      <div className="mt-0.5">{icons[toast.type]}</div>
      <div className="flex-1">
        {toast.title && <div className="font-semibold">{toast.title}</div>}
        <div className="text-sm">{toast.message}</div>
      </div>
      <button
        type="button"
        onClick={onClose}
        aria-label="Close"
        className="rounded p-1 hover:bg-black/5 focus:outline-none focus:ring-2 focus:ring-offset-1"
      >
        <svg className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden>
          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </div>
  )
}
