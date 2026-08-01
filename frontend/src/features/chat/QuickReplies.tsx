type QuickRepliesProps = {
  replies: string[]
  disabled?: boolean
  onSelect: (label: string) => void
}

export function QuickReplies({
  replies,
  disabled = false,
  onSelect,
}: QuickRepliesProps) {
  if (!replies.length) return null

  return (
    <div
      className="flex flex-wrap gap-2 px-1 pb-2"
      role="group"
      aria-label="Hızlı cevap seçenekleri"
      data-testid="quick-replies"
    >
      {replies.map((label) => (
        <button
          key={label}
          type="button"
          disabled={disabled}
          onClick={() => onSelect(label)}
          className={[
            'rounded-full border border-equa-primary/40 bg-equa-accent-soft',
            'px-3 py-1.5 text-xs font-medium text-equa-primary',
            'transition hover:bg-equa-primary/20 focus-ring',
            'disabled:cursor-not-allowed disabled:opacity-50',
          ].join(' ')}
        >
          {label}
        </button>
      ))}
    </div>
  )
}
