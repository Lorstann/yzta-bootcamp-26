export type ChatRole = 'user' | 'assistant'

export type ChatMessage = {
  id: string
  role: ChatRole
  content: string
  streaming?: boolean
}

export type ChatStatus = 'idle' | 'streaming' | 'error'
