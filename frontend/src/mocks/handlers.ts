import { http, HttpResponse, delay } from 'msw'
import {
  MOCK_CHAT_CHUNKS,
  MOCK_WEEKLY_TASKS,
  encodeSse,
} from './data/chat-fixtures'

const API = 'http://localhost:8000'

export const handlers = [
  http.get(`${API}/api/v1/health`, () => {
    return HttpResponse.json({
      success: true,
      data: { status: 'healthy' },
      error: null,
      meta: {},
    })
  }),

  http.post(`${API}/api/v1/chat/stream`, async ({ request }) => {
    const body = (await request.json()) as { message?: string }

    if (body.message?.trim().toLowerCase() === 'error') {
      const stream = new ReadableStream<Uint8Array>({
        start(controller) {
          const encoder = new TextEncoder()
          controller.enqueue(
            encoder.encode(
              encodeSse({
                type: 'error',
                message: 'AI servisi şu an yanıt veremiyor.',
              }),
            ),
          )
          controller.close()
        },
      })

      return new HttpResponse(stream, {
        status: 200,
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
        },
      })
    }

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        const encoder = new TextEncoder()
        for (const chunk of MOCK_CHAT_CHUNKS) {
          await delay(60)
          controller.enqueue(
            encoder.encode(encodeSse({ type: 'chunk', data: chunk })),
          )
        }
        await delay(40)
        controller.enqueue(
          encoder.encode(
            encodeSse({
              type: 'done',
              guardrail_triggered: false,
              guardrail_category: null,
              weekly_tasks: [...MOCK_WEEKLY_TASKS],
            }),
          ),
        )
        controller.close()
      },
    })

    return new HttpResponse(stream, {
      status: 200,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
    })
  }),
]
