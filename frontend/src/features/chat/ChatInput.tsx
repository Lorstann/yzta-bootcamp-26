import { useState, type FormEvent } from 'react'
import { Send } from 'lucide-react'
import { Button } from '@/components/ui'

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
      className="flex items-center gap-3 rounded-xl border border-equa-line/40 bg-[#0A0A14] px-3 py-2 shadow-inner focus-within:border-equa-primary"
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
        placeholder="AI Koçuna mesaj yaz…"
        className="min-h-[44px] max-h-32 flex-1 resize-none border-none bg-transparent px-2 py-2 text-sm text-equa-ink placeholder:text-equa-outline focus:outline-none focus:ring-0 disabled:opacity-60"
      />
      <Button
        type="submit"
        variant="primary"
        disabled={disabled || !value.trim()}
        className="!min-h-10 !rounded-lg !px-3 !py-2"
      >
        <Send size={18} aria-hidden />
        Gönder
      </Button>
    </form>
  )
}
