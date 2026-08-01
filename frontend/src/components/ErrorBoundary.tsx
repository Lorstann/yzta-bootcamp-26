import { Component, type ErrorInfo, type ReactNode } from 'react'

type Props = { children: ReactNode }
type State = { hasError: boolean }

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    // Keep console for unexpected render failures in production debugging
    console.error('Equa UI error', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="mx-auto flex min-h-full max-w-md flex-col justify-center px-4 py-10 text-center">
          <h1 className="font-display text-lg font-semibold text-equa-ink">
            Bir şeyler ters gitti
          </h1>
          <p className="mt-2 text-sm text-equa-muted">
            Sayfayı yenilemeyi dene. Sorun sürerse mentörüne haber ver.
          </p>
          <button
            type="button"
            className="mt-6 rounded-xl bg-gradient-to-r from-equa-primary-container to-equa-primary px-4 py-2.5 text-sm font-bold text-equa-on-primary"
            onClick={() => window.location.assign('/dashboard')}
          >
            Sohbete dön
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
