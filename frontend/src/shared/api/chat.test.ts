import { describe, expect, it } from 'vitest'
import { streamChat } from './chat'
import { getHealth } from './health'
import { MOCK_CHAT_CHUNKS, MOCK_WEEKLY_TASKS } from '../../mocks/data/chat-fixtures'

describe('API client with MSW', () => {
  it('getHealth returns envelope data', async () => {
    const health = await getHealth()
    expect(health).toEqual({ status: 'healthy' })
  })

  it('streamChat yields mock chunks then done', async () => {
    const chunks: string[] = []
    let doneTasks: string[] | null = null

    for await (const event of streamChat({
      tenant_id: '11111111-1111-1111-1111-111111111111',
      session_id: '22222222-2222-2222-2222-222222222222',
      message: 'Merhaba',
    })) {
      if (event.type === 'chunk') {
        chunks.push(event.data)
      }
      if (event.type === 'done') {
        doneTasks = event.weekly_tasks
      }
    }

    expect(chunks).toEqual([...MOCK_CHAT_CHUNKS])
    expect(doneTasks).toEqual([...MOCK_WEEKLY_TASKS])
  })

  it('streamChat surfaces SSE error events for message "error"', async () => {
    const events = []
    for await (const event of streamChat({
      tenant_id: '11111111-1111-1111-1111-111111111111',
      session_id: '22222222-2222-2222-2222-222222222222',
      message: 'error',
    })) {
      events.push(event)
    }

    expect(events).toEqual([
      { type: 'error', message: 'AI servisi şu an yanıt veremiyor.' },
    ])
  })
})
