import { useState, type FormEvent } from 'react'

type ChatInputProps = {
  disabled?: boolean
  onSend: (message: string) => void
}

export function ChatInput({ disabled = false, onSend }: ChatInputProps) {
  const [value, setValue] = useState('')

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2"
      data-testid="chat-input-form"
    >
      <label htmlFor="chat-message" className="sr-only">
        Mesajın
      </label>
      <textarea
        id="chat-message"
        rows={1}
        value={value}
        disabled={disabled}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSubmit(e)
          }
        }}
        placeholder="Mesaj yaz…"
        className="min-h-[44px] max-h-32 flex-1 resize-none rounded-xl border border-equa-line bg-white/80 px-3 py-2.5 text-sm text-equa-ink placeholder:text-equa-muted focus:border-equa-accent focus:outline-none focus:ring-2 focus:ring-equa-accent/30 disabled:opacity-60"
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        className="shrink-0 rounded-xl bg-equa-accent px-4 py-2.5 text-sm font-medium text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40"
      >
        Gönder
      </button>
    </form>
  )
}
