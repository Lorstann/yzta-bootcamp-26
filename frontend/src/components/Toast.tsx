import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

type Toast = { id: string; message: string }

type ToastCtx = {
  push: (message: string) => void
}

const Ctx = createContext<ToastCtx | null>(null)

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const push = useCallback((message: string) => {
    const id = crypto.randomUUID()
    setToasts((prev) => [...prev, { id, message }])
    window.setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3500)
  }, [])

  const value = useMemo(() => ({ push }), [push])

  return (
    <Ctx.Provider value={value}>
      {children}
      <div
        className="pointer-events-none fixed bottom-20 left-1/2 z-[60] flex w-full max-w-sm -translate-x-1/2 flex-col gap-2 px-4 lg:bottom-6"
        aria-live="polite"
      >
        {toasts.map((t) => (
          <div
            key={t.id}
            className="rounded-xl border border-equa-line/40 bg-equa-surface-high/95 px-3 py-2 text-center text-sm text-equa-ink shadow-lg backdrop-blur-md animate-[fadeSlide_220ms_ease-out]"
          >
            {t.message}
          </div>
        ))}
      </div>
    </Ctx.Provider>
  )
}

/** Hook colocated with ToastProvider (react-refresh limitation). */
// eslint-disable-next-line react-refresh/only-export-components
export function useToast(): ToastCtx {
  const ctx = useContext(Ctx)
  if (!ctx) {
    return { push: () => undefined }
  }
  return ctx
}
