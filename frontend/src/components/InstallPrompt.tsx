import { useEffect, useState } from 'react'
import { Button } from '@/components/ui'

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>
}

export function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(
    null,
  )
  const [dismissed, setDismissed] = useState(false)

  useEffect(() => {
    const handler = (e: Event) => {
      e.preventDefault()
      setDeferred(e as BeforeInstallPromptEvent)
    }
    window.addEventListener('beforeinstallprompt', handler)
    return () => window.removeEventListener('beforeinstallprompt', handler)
  }, [])

  if (!deferred || dismissed) return null

  return (
    <div className="glass-panel fixed bottom-20 left-1/2 z-40 w-[min(100%-1.5rem,24rem)] -translate-x-1/2 rounded-2xl p-3 shadow-lg lg:bottom-6">
      <p className="text-sm text-equa-ink">
        Equa’yı ana ekrana ekle — tarayıcı çubuğu olmadan açılır.
      </p>
      <div className="mt-2 flex gap-2">
        <Button
          className="flex-1"
          onClick={async () => {
            await deferred.prompt()
            setDismissed(true)
            setDeferred(null)
          }}
        >
          Yükle
        </Button>
        <Button variant="ghost" onClick={() => setDismissed(true)}>
          Sonra
        </Button>
      </div>
    </div>
  )
}
