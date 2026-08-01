import { useEffect, useState } from 'react'

export function OfflineBanner() {
  const [offline, setOffline] = useState(
    typeof navigator !== 'undefined' ? !navigator.onLine : false,
  )

  useEffect(() => {
    const on = () => setOffline(false)
    const off = () => setOffline(true)
    window.addEventListener('online', on)
    window.addEventListener('offline', off)
    return () => {
      window.removeEventListener('online', on)
      window.removeEventListener('offline', off)
    }
  }, [])

  if (!offline) return null

  return (
    <div
      className="border-b border-amber-500/30 bg-amber-500/15 px-4 py-2 text-center text-sm text-amber-200"
      role="status"
    >
      Çevrimdışısın — sohbet için bağlantı gerekli. Shell önbellekte kalır.
    </div>
  )
}
