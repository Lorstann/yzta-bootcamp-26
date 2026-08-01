const MOODS = [
  { score: 1, emoji: '😫', label: 'Çok Kötü' },
  { score: 2, emoji: '😕', label: 'Kötü' },
  { score: 3, emoji: '😐', label: 'Normal' },
  { score: 4, emoji: '🙂', label: 'İyi' },
  { score: 5, emoji: '🤩', label: 'Çok İyi' },
] as const

export { MOODS }

type MoodSelectorProps = {
  value: number | null
  onSelect: (score: number) => void
  disabled?: boolean
  error?: string | null
}

export function MoodSelector({
  value,
  onSelect,
  disabled = false,
  error = null,
}: MoodSelectorProps) {
  return (
    <div>
      <div className="flex items-center justify-between px-1 py-6">
        {MOODS.map((m) => {
          const selected = value === m.score
          return (
            <button
              key={m.score}
              type="button"
              aria-label={m.label}
              aria-pressed={selected}
              disabled={disabled}
              onClick={() => onSelect(m.score)}
              className={[
                'transition-all duration-300',
                selected
                  ? 'relative z-10 scale-125 text-5xl drop-shadow-[0_0_15px_rgba(207,188,255,0.6)]'
                  : 'scale-100 text-3xl opacity-40 grayscale hover:scale-125 hover:opacity-100 hover:grayscale-0',
                disabled ? 'cursor-not-allowed' : '',
              ].join(' ')}
            >
              {selected ? (
                <span className="absolute inset-0 -z-10 scale-150 rounded-full bg-equa-primary/20 blur-xl" />
              ) : null}
              {m.emoji}
            </button>
          )
        })}
      </div>
      {error ? (
        <p className="text-center text-sm text-red-300" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}
