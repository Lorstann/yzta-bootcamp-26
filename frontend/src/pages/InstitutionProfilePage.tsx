import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'
import { zodResolver } from '@hookform/resolvers/zod'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { apiGet, apiPatch } from '@/shared/api/client'
import { queryKeys } from '@/shared/api/query-keys'
import { Button, Card, Input, StatCard } from '@/components/ui'

type StaffMe = {
  id: string
  email: string
  full_name: string | null
  role: string
  tenant: {
    id: string
    name: string
    slug: string
    revenue_per_student: number | null
  }
}

type Usage = {
  total_students: number
  active_students_7d: number
  adoption_rate_7d: number
  total_tasks: number
  completed_tasks: number
  task_completion_rate: number
}

const settingsSchema = z.object({
  revenue_per_student: z
    .number()
    .positive('0’dan büyük olmalı')
    .max(1_000_000, 'En fazla 1.000.000'),
})

type SettingsForm = z.infer<typeof settingsSchema>

const roleLabel: Record<string, string> = {
  instructor: 'Eğitmen',
  admin: 'Yönetici',
}

function pct(rate: number): string {
  return `%${Math.round(rate * 100)}`
}

export function InstitutionProfilePage() {
  const queryClient = useQueryClient()
  const [saveMsg, setSaveMsg] = useState<string | null>(null)

  const meQuery = useQuery({
    queryKey: queryKeys.institution.me(),
    queryFn: () => apiGet<StaffMe>('/api/v1/institution/me'),
  })
  const usageQuery = useQuery({
    queryKey: queryKeys.institution.usage(),
    queryFn: () => apiGet<Usage>('/api/v1/institution/usage'),
  })

  const me = meQuery.data
  const usage = usageQuery.data
  const isAdmin = me?.role === 'admin'

  const form = useForm<SettingsForm>({
    resolver: zodResolver(settingsSchema),
    values: {
      revenue_per_student: me?.tenant.revenue_per_student ?? 5000,
    },
  })

  const saveMutation = useMutation({
    mutationFn: (values: SettingsForm) =>
      apiPatch<{ revenue_per_student: number }>(
        '/api/v1/institution/settings',
        { revenue_per_student: values.revenue_per_student },
      ),
    onSuccess: () => {
      setSaveMsg('Ayarlar kaydedildi.')
      void queryClient.invalidateQueries({ queryKey: queryKeys.institution.me() })
      void queryClient.invalidateQueries({ queryKey: queryKeys.institution.roi() })
      void queryClient.invalidateQueries({
        queryKey: queryKeys.institution.overview(),
      })
    },
    onError: (err: Error) => {
      setSaveMsg(err.message || 'Kayıt başarısız.')
    },
  })

  const loading = meQuery.isLoading || usageQuery.isLoading
  const error =
    meQuery.error instanceof Error
      ? meQuery.error.message
      : usageQuery.error instanceof Error
        ? usageQuery.error.message
        : null

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-6">
        <p className="text-sm text-red-300" role="alert">
          {error}
        </p>
        <button
          type="button"
          className="mt-3 text-sm font-medium text-equa-primary underline"
          onClick={() => {
            void meQuery.refetch()
            void usageQuery.refetch()
          }}
        >
          Yeniden dene
        </button>
      </div>
    )
  }

  if (loading && !me) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-6" aria-busy="true">
        <div className="h-8 w-48 animate-pulse rounded-lg bg-equa-line/40" />
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 animate-pulse rounded-2xl bg-equa-line/40" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <h1 className="font-display text-xl font-semibold text-equa-ink">
        Kurum Profili
      </h1>
      <p className="mt-1 text-sm text-equa-muted">
        Hesap bilgilerin ve tenant adoption metrikleri.
      </p>

      {me ? (
        <Card className="mt-6 space-y-3">
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">Ad</p>
            <p className="font-medium text-equa-ink">
              {me.full_name || '—'}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              E-posta
            </p>
            <p className="font-medium text-equa-ink">{me.email}</p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">Rol</p>
            <p className="font-medium text-equa-ink">
              {roleLabel[me.role] ?? me.role}
            </p>
          </div>
          <div>
            <p className="text-xs uppercase tracking-wide text-equa-muted">
              Kurum
            </p>
            <p className="font-medium text-equa-ink">
              {me.tenant.name}{' '}
              <span className="text-equa-muted">({me.tenant.slug})</span>
            </p>
          </div>
        </Card>
      ) : null}

      {usage ? (
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <StatCard
            label="Öğrenci"
            value={String(usage.total_students)}
            delta={`Aktif (7g): ${usage.active_students_7d}`}
          />
          <StatCard
            label="Adoption (7g)"
            value={pct(usage.adoption_rate_7d)}
          />
          <StatCard
            label="Görevler"
            value={`${usage.completed_tasks}/${usage.total_tasks}`}
            delta={`Tamamlanma: ${pct(usage.task_completion_rate)}`}
          />
        </div>
      ) : null}

      {isAdmin ? (
        <Card className="mt-8">
          <h2 className="font-display text-base font-semibold text-equa-ink">
            Tenant ayarları
          </h2>
          <p className="mt-1 text-sm text-equa-muted">
            Öğrenci başına gelir (ROI hesabı için).
          </p>
          <form
            className="mt-4 space-y-3"
            onSubmit={form.handleSubmit((values) => {
              setSaveMsg(null)
              saveMutation.mutate(values)
            })}
          >
            <div>
              <label
                htmlFor="revenue_per_student"
                className="text-sm font-medium text-equa-ink"
              >
                Öğrenci başına gelir (TRY)
              </label>
              <Input
                id="revenue_per_student"
                type="number"
                step="1"
                min="1"
                className="mt-1"
                {...form.register('revenue_per_student', { valueAsNumber: true })}
              />
              {form.formState.errors.revenue_per_student?.message ? (
                <p className="mt-1 text-sm text-red-300" role="alert">
                  {form.formState.errors.revenue_per_student.message}
                </p>
              ) : null}
            </div>
            {saveMsg ? (
              <p className="text-sm text-equa-muted" role="status">
                {saveMsg}
              </p>
            ) : null}
            <Button type="submit" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Kaydediliyor…' : 'Kaydet'}
            </Button>
          </form>
        </Card>
      ) : null}
    </div>
  )
}
