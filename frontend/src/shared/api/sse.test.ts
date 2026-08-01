import { describe, expect, it } from 'vitest'
import { parseSse, type ChatSseEvent } from './sse'

function streamFromString(text: string): ReadableStream<Uint8Array> {
  const encoder = new TextEncoder()
  return new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(text))
      controller.close()
    },
  })
}

describe('parseSse', () => {
  it('parses chunk, done, and error events', async () => {
    const sse =
      'data: {"type":"chunk","data":"Merhaba "}\n\n' +
      'data: {"type":"done","guardrail_triggered":false,"guardrail_category":null,"daily_tasks":["görev 1"]}\n\n' +
      'data: {"type":"error","message":"bozuk"}\n\n'

    const events: ChatSseEvent[] = []
    for await (const event of parseSse(streamFromString(sse))) {
      events.push(event)
    }

    expect(events).toEqual([
      { type: 'chunk', data: 'Merhaba ' },
      {
        type: 'done',
        guardrail_triggered: false,
        guardrail_category: null,
        daily_tasks: ['görev 1'],
      },
      { type: 'error', message: 'bozuk' },
    ])
  })

  it('skips malformed payloads', async () => {
    const sse =
      'data: not-json\n\n' +
      'data: {"type":"chunk","data":"ok"}\n\n'

    const events: ChatSseEvent[] = []
    for await (const event of parseSse(streamFromString(sse))) {
      events.push(event)
    }

    expect(events).toEqual([{ type: 'chunk', data: 'ok' }])
  })
})
