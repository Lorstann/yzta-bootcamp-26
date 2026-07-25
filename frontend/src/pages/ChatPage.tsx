export function ChatPage() {
  return (
    <div className="mx-auto flex h-full min-h-0 w-full max-w-3xl flex-col px-4 py-4 lg:max-w-4xl lg:px-8 lg:py-6">
      <div className="mb-3 shrink-0 lg:mb-4">
        <h1 className="font-display text-lg font-semibold text-equa-ink lg:text-xl">
          Sohbet
        </h1>
        <p className="mt-0.5 text-sm text-equa-muted">
          AI koçunla kısa bir check-in yap.
        </p>
      </div>

      <section
        className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden rounded-2xl border border-equa-line/70 bg-equa-surface/60"
        aria-label="Sohbet alanı"
      >
        <div
          className="min-h-0 flex-1 overflow-y-auto px-4 py-6"
          data-testid="chat-message-slot"
        >
          <div className="flex h-full min-h-[12rem] flex-col items-center justify-center text-center">
            <p className="font-display text-base font-medium text-equa-ink">
              Chat yakında
            </p>
            <p className="mt-2 max-w-xs text-sm text-equa-muted">
              Mesaj listesi ve streaming yanıtlar bir sonraki adımda eklenecek.
            </p>
          </div>
        </div>

        <div
          className="shrink-0 border-t border-equa-line/60 px-3 py-3 lg:px-4"
          data-testid="chat-input-slot"
          aria-label="Mesaj yazma alanı"
        >
          <div className="flex items-center gap-2 rounded-xl border border-dashed border-equa-line bg-white/50 px-3 py-3 text-sm text-equa-muted">
            Mesaj yaz… (F5)
          </div>
        </div>
      </section>
    </div>
  )
}
