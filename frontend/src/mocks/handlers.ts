import { http, HttpResponse, delay } from 'msw'
import {
  MOCK_CHAT_CHUNKS,
  MOCK_DAILY_TASKS,
  encodeSse,
} from './data/chat-fixtures'

const API = 'http://localhost:8000'

const MOCK_SESSION_ID = '00000000-0000-4000-8000-000000000010'

export const handlers = [
  http.get(`${API}/api/v1/health`, () => {
    return HttpResponse.json({
      success: true,
      data: { status: 'healthy' },
      error: null,
      meta: {},
    })
  }),

  http.post(`${API}/api/v1/auth/login`, async ({ request }) => {
    const body = (await request.json()) as {
      email?: string
      password?: string
      tenant_slug?: string
    }
    if (!body.email || !body.password) {
      return HttpResponse.json(
        {
          success: false,
          data: null,
          error: { code: 'VALIDATION_ERROR', message: 'Invalid credentials', details: [] },
          meta: {},
        },
        { status: 401 },
      )
    }
    const role = body.email.includes('instructor') ? 'instructor' : 'student'
    return HttpResponse.json({
      success: true,
      data: {
        access_token: 'mock-token',
        token_type: 'bearer',
        user: {
          id: '11111111-1111-1111-1111-111111111101',
          tenant_id: '11111111-1111-1111-1111-111111111111',
          email: body.email,
          full_name: 'Mock User',
          role,
        },
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/checkins/current`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: MOCK_SESSION_ID,
        checkin_date: '2026-07-28',
        status: 'in_progress',
        summary: null,
        mood_score: null,
        energy_level: null,
        motivation_level: null,
        stage: 'opening',
        turn_count: 0,
        quick_replies: [
          'Tükendim',
          'Yorgunum',
          'İdare eder',
          'İyiyim',
          'Turbo moddayım',
        ],
        messages: [],
        daily_tasks: [],
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/checkins/history`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        sessions: [
          {
            id: MOCK_SESSION_ID,
            checkin_date: '2026-07-28',
            status: 'in_progress',
            summary: null,
            mood_score: 4,
            task_count: 2,
            completed_task_count: 1,
          },
        ],
      },
      error: null,
      meta: {},
    })
  }),

  http.patch(`${API}/api/v1/checkins/current/mood`, async ({ request }) => {
    const body = (await request.json()) as { mood_score?: number }
    return HttpResponse.json({
      success: true,
      data: {
        id: MOCK_SESSION_ID,
        checkin_date: '2026-07-28',
        status: 'in_progress',
        summary: null,
        mood_score: body.mood_score ?? 3,
        messages: [],
        daily_tasks: [],
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/tasks`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        tasks: [
          {
            id: '00000000-0000-4000-8000-000000000101',
            title: 'React Hooks okuması',
            description: null,
            is_completed: false,
            completed_at: null,
            status: 'active',
            due_date: '2026-07-30',
            checkin_date: '2026-07-28',
            checkin_session_id: MOCK_SESSION_ID,
          },
        ],
      },
      error: null,
      meta: {},
    })
  }),

  http.patch(`${API}/api/v1/tasks/:taskId`, async ({ params }) => {
    return HttpResponse.json({
      success: true,
      data: {
        id: params.taskId,
        title: 'Mock task',
        is_completed: true,
        completed_at: new Date().toISOString(),
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/profiles/me`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        user_id: '11111111-1111-1111-1111-111111111101',
        capacity_score: 70,
        linkedin_url: null,
        bio: null,
        competencies: null,
        city: 'İzmir',
        district: 'Bornova',
        program_track: 'Veri Bilimi',
        interests: {
          hobbies: ['Yürüyüş', 'Kitap'],
          recharge: ['Doğada olmak'],
          notes: [],
        },
        onboarding_completed: true,
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/profiles/me/stats`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_checkins: 3,
        streak_days: 2,
        completed_tasks: 5,
        open_tasks: 1,
        capacity_history: [
          { score: 65, recorded_at: '2026-07-01T00:00:00Z' },
          { score: 70, recorded_at: '2026-07-15T00:00:00Z' },
        ],
      },
      error: null,
      meta: {},
    })
  }),

  http.patch(`${API}/api/v1/profiles/me/onboarding`, async ({ request }) => {
    const body = (await request.json()) as Record<string, unknown>
    return HttpResponse.json({
      success: true,
      data: {
        user_id: '11111111-1111-1111-1111-111111111101',
        capacity_score: body.capacity_score ?? 70,
        linkedin_url: null,
        bio: body.bio ?? null,
        competencies: null,
        city: body.city ?? null,
        district: body.district ?? null,
        program_track: body.program_track ?? null,
        interests: body.interests ?? { hobbies: [], recharge: [], notes: [] },
        onboarding_completed: body.onboarding_completed ?? true,
      },
      error: null,
      meta: {},
    })
  }),

  http.post(`${API}/api/v1/profiles/me/linkedin`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        competencies: {
          skills: ['Python', 'React'],
          summary: 'Mock LinkedIn extract',
          experience_years: 2,
        },
        source: 'heuristic',
        fallback_required: false,
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/institution/students`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        students: [
          {
            user_id: '11111111-1111-1111-1111-111111111101',
            full_name: 'Ayşe Demir',
            email: 'ayse@example.com',
            risk_level: 'red',
            rationale: 'Check-in kaçırıldı ve görev tamamlanma oranı düşük.',
            metrics: {
              task_completion_rate: 0.2,
              capacity_score: 35,
              missed_checkin: true,
              open_tasks: 2,
            },
            capacity_score: 35,
            updated_at: '2026-07-30T12:00:00Z',
          },
          {
            user_id: '11111111-1111-1111-1111-111111111102',
            full_name: 'Mehmet Kaya',
            email: 'mehmet@example.com',
            risk_level: 'green',
            rationale: 'Check-in ve görev metrikleri stabil.',
            metrics: {
              task_completion_rate: 0.9,
              capacity_score: 80,
              missed_checkin: false,
              open_tasks: 1,
            },
            capacity_score: 80,
            updated_at: '2026-07-30T12:00:00Z',
          },
        ],
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/institution/roi`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        prevented_dropouts: 2,
        protected_revenue: 10000,
        revenue_per_student: 5000,
        active_high_risk: 1,
        total_students: 2,
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/institution/overview`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_students: 2,
        checked_in_today: 1,
        daily_checkin_rate: 0.5,
        avg_capacity: 57.5,
        risk_distribution: { green: 1, yellow: 0, red: 1 },
        trend_7d: [],
        roi: {
          prevented_dropouts: 2,
          protected_revenue: 10000,
          revenue_per_student: 5000,
          active_high_risk: 1,
          total_students: 2,
        },
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/institution/me`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        id: '11111111-1111-1111-1111-111111111201',
        email: 'coordinator@equa.dev',
        full_name: 'Coord',
        role: 'instructor',
        tenant: {
          id: '11111111-1111-1111-1111-111111111111',
          name: 'Equa Demo',
          slug: 'equa-demo',
          revenue_per_student: 5000,
        },
      },
      error: null,
      meta: {},
    })
  }),

  http.get(`${API}/api/v1/institution/usage`, () => {
    return HttpResponse.json({
      success: true,
      data: {
        total_students: 2,
        active_students_7d: 1,
        adoption_rate_7d: 0.5,
        total_tasks: 10,
        completed_tasks: 6,
        task_completion_rate: 0.6,
      },
      error: null,
      meta: {},
    })
  }),

  http.patch(`${API}/api/v1/institution/settings`, async ({ request }) => {
    const body = (await request.json()) as { revenue_per_student?: number }
    return HttpResponse.json({
      success: true,
      data: {
        id: '11111111-1111-1111-1111-111111111111',
        name: 'Equa Demo',
        slug: 'equa-demo',
        revenue_per_student: body.revenue_per_student ?? 5000,
      },
      error: null,
      meta: {},
    })
  }),

  http.post(`${API}/api/v1/institution/assistant/stream`, async ({ request }) => {
    const auth = request.headers.get('Authorization')
    if (!auth) {
      return HttpResponse.json(
        {
          success: false,
          data: null,
          error: {
            code: 'UNAUTHENTICATED',
            message: 'Authentication required',
            details: [],
          },
          meta: {},
        },
        { status: 401 },
      )
    }

    const stream = new ReadableStream<Uint8Array>({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(
          encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', data: 'Metrik özeti: ' })}\n\n`,
          ),
        )
        controller.enqueue(
          encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', data: '1 kırmızı risk.' })}\n\n`,
          ),
        )
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: 'done' })}\n\n`),
        )
        controller.close()
      },
    })

    return new HttpResponse(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
      },
    })
  }),

  http.post(`${API}/api/v1/chat/stream`, async ({ request }) => {
    const auth = request.headers.get('Authorization')
    if (!auth) {
      return HttpResponse.json(
        {
          success: false,
          data: null,
          error: {
            code: 'UNAUTHENTICATED',
            message: 'Authentication required',
            details: [],
          },
          meta: {},
        },
        { status: 401 },
      )
    }

    const body = (await request.json()) as { message?: string; session_id?: string }

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

    const isGuardrail = body.message?.toLowerCase().includes('intihar')
    const lowered = body.message?.toLowerCase() ?? ''
    const isOffTopic =
      lowered.includes('makarna tarifi') ||
      lowered.includes('dünya savaşı') ||
      lowered.includes('dunya savasi')

    const stream = new ReadableStream<Uint8Array>({
      async start(controller) {
        const encoder = new TextEncoder()
        if (isGuardrail) {
          controller.enqueue(
            encoder.encode(
              encodeSse({
                type: 'chunk',
                data: 'Duygularını paylaştığın için teşekkür ederim. ',
              }),
            ),
          )
          controller.enqueue(
            encoder.encode(
            encodeSse({
              type: 'done',
              guardrail_triggered: true,
              guardrail_category: 'critical',
              daily_tasks: null,
              checkin_completed: false,
              state: null,
              mode: 'checkin',
              quick_replies: null,
              off_topic: false,
              scope_family: null,
            }),
          ),
        )
        controller.close()
        return
      }

      if (isOffTopic) {
        const leisure = lowered.includes('tarif')
        controller.enqueue(
          encoder.encode(
            encodeSse({
              type: 'chunk',
              data: leisure
                ? 'Tarif vermiyorum ama bunu bugünün molası olarak planlayabiliriz. '
                : 'Bu Equa kapsamı dışında — eğitim veya dinlenme planına dönelim. ',
            }),
          ),
        )
        controller.enqueue(
          encoder.encode(
            encodeSse({
              type: 'done',
              guardrail_triggered: false,
              guardrail_category: null,
              daily_tasks: null,
              checkin_completed: false,
              state: null,
              stage: 'opening',
              turn_count: 0,
              mode: 'checkin',
              quick_replies: ['Tükendim', 'Yorgunum', 'İdare eder', 'İyiyim', 'Turbo'],
              off_topic: true,
              scope_family: leisure ? 'leisure' : 'hard',
            }),
          ),
        )
        controller.close()
        return
      }

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
            daily_tasks: [...MOCK_DAILY_TASKS],
            checkin_completed: true,
            state: {
              enerji: 6,
              motivasyon: 5,
              engel: null,
              yuk: 'orta',
              hazir: true,
            },
            stage: 'completed',
            turn_count: 3,
            mode: 'checkin',
            quick_replies: null,
            off_topic: false,
            scope_family: null,
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
