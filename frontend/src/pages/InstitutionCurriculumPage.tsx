import { useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { BookOpen, Trash2, Upload } from 'lucide-react'
import { Button, Card, Input } from '@/components/ui'
import {
  createCurriculumText,
  deleteCurriculum,
  listCurricula,
  uploadCurriculumFile,
  type CurriculumItem,
} from '@/shared/api/institution'
import { queryKeys } from '@/shared/api/query-keys'
import { ApiClientError } from '@/shared/api/envelope'
import { getStoredUser } from '@/shared/auth/storage'

export function InstitutionCurriculumPage() {
  const user = getStoredUser()
  const isAdmin = user?.role === 'admin'
  const queryClient = useQueryClient()
  const [title, setTitle] = useState('')
  const [pasteTitle, setPasteTitle] = useState('')
  const [pasteText, setPasteText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [formError, setFormError] = useState<string | null>(null)

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.institution.curriculum(),
    queryFn: listCurricula,
  })

  const invalidate = () =>
    queryClient.invalidateQueries({
      queryKey: queryKeys.institution.curriculum(),
    })

  const uploadMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('Dosya seçilmedi')
      return uploadCurriculumFile(file, title || undefined)
    },
    onSuccess: async () => {
      setFile(null)
      setTitle('')
      setFormError(null)
      await invalidate()
    },
    onError: (err: unknown) => {
      setFormError(
        err instanceof ApiClientError
          ? err.message
          : 'Yükleme başarısız oldu.',
      )
    },
  })

  const pasteMutation = useMutation({
    mutationFn: () =>
      createCurriculumText({
        title: pasteTitle.trim(),
        text: pasteText.trim(),
      }),
    onSuccess: async () => {
      setPasteTitle('')
      setPasteText('')
      setFormError(null)
      await invalidate()
    },
    onError: (err: unknown) => {
      setFormError(
        err instanceof ApiClientError
          ? err.message
          : 'Metin kaydı başarısız oldu.',
      )
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteCurriculum(id),
    onSuccess: async () => {
      await invalidate()
    },
  })

  const rows = useMemo(() => data ?? [], [data])

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 p-4 lg:p-6">
      <header>
        <h1 className="font-display text-2xl font-bold text-equa-ink">
          Müfredat
        </h1>
        <p className="mt-1 text-sm text-equa-muted">
          Öğrenci AI koçu yalnızca yüklediğin müfredat bağlamında teknik görev
          önerir. PDF, DOCX, TXT veya MD yükleyebilir ya da metin yapıştırabilirsin.
        </p>
      </header>

      {isAdmin ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="space-y-3 p-4">
            <h2 className="flex items-center gap-2 text-sm font-bold text-equa-ink">
              <Upload size={16} aria-hidden />
              Dosya yükle
            </h2>
            <label className="block text-xs font-medium text-equa-muted">
              Başlık (opsiyonel)
              <Input
                className="mt-1"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Örn. React Bootcamp Syllabus"
              />
            </label>
            <label className="block text-xs font-medium text-equa-muted">
              Dosya (.pdf .docx .txt .md)
              <input
                type="file"
                accept=".pdf,.docx,.txt,.md,application/pdf,text/plain,text/markdown,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                className="mt-1 block w-full text-sm text-equa-ink file:mr-3 file:rounded-lg file:border-0 file:bg-equa-accent-soft file:px-3 file:py-2 file:text-equa-primary"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
              />
            </label>
            {file ? (
              <p className="text-xs text-equa-muted">{file.name}</p>
            ) : null}
            <Button
              disabled={!file || uploadMutation.isPending}
              onClick={() => uploadMutation.mutate()}
            >
              {uploadMutation.isPending ? 'Yükleniyor…' : 'Yükle ve indeksle'}
            </Button>
          </Card>

          <Card className="space-y-3 p-4">
            <h2 className="flex items-center gap-2 text-sm font-bold text-equa-ink">
              <BookOpen size={16} aria-hidden />
              Metin yapıştır
            </h2>
            <label className="block text-xs font-medium text-equa-muted">
              Başlık
              <Input
                className="mt-1"
                value={pasteTitle}
                onChange={(e) => setPasteTitle(e.target.value)}
                placeholder="Müfredat başlığı"
                required
              />
            </label>
            <label className="block text-xs font-medium text-equa-muted">
              İçerik
              <textarea
                value={pasteText}
                onChange={(e) => setPasteText(e.target.value)}
                rows={8}
                className="mt-1 w-full rounded-xl border border-equa-line/40 bg-equa-surface px-3 py-2 text-sm text-equa-ink focus-ring"
                placeholder="Haftalık konular, öğrenme çıktıları…"
              />
            </label>
            <Button
              disabled={
                !pasteTitle.trim() ||
                !pasteText.trim() ||
                pasteMutation.isPending
              }
              onClick={() => pasteMutation.mutate()}
            >
              {pasteMutation.isPending ? 'Kaydediliyor…' : 'Kaydet ve indeksle'}
            </Button>
          </Card>
        </div>
      ) : (
        <Card className="p-4 text-sm text-equa-muted">
          Müfredat yükleme yalnızca kurum adminleri için açıktır. Listeyi
          görüntüleyebilirsin.
        </Card>
      )}

      {formError ? (
        <p className="text-sm text-red-300" role="alert">
          {formError}
        </p>
      ) : null}

      <section aria-label="Yüklü müfredatlar">
        <h2 className="mb-3 font-display text-lg font-bold text-equa-ink">
          Yüklü müfredatlar
        </h2>
        {isLoading ? (
          <p className="text-sm text-equa-muted">Yükleniyor…</p>
        ) : error ? (
          <p className="text-sm text-red-300" role="alert">
            Liste alınamadı.
          </p>
        ) : rows.length === 0 ? (
          <Card className="p-4 text-sm text-equa-muted">
            Henüz müfredat yok. İlk dosyayı yükleyerek öğrenci koçuna bağlam
            ver.
          </Card>
        ) : (
          <ul className="space-y-3">
            {rows.map((item: CurriculumItem) => (
              <li key={item.id}>
                <Card className="flex items-start justify-between gap-3 p-4">
                  <div className="min-w-0">
                    <p className="font-medium text-equa-ink">{item.title}</p>
                    <p className="mt-1 text-xs text-equa-muted">
                      {item.source_type}
                      {item.file_name ? ` · ${item.file_name}` : ''}
                      {item.chunk_count != null
                        ? ` · ${item.chunk_count} parça`
                        : ''}
                      {item.created_at
                        ? ` · ${new Date(item.created_at).toLocaleDateString('tr-TR')}`
                        : ''}
                    </p>
                  </div>
                  {isAdmin ? (
                    <Button
                      variant="ghost"
                      className="shrink-0"
                      disabled={deleteMutation.isPending}
                      onClick={() => {
                        if (
                          window.confirm(
                            `"${item.title}" müfredatını pasife almak istiyor musun?`,
                          )
                        ) {
                          deleteMutation.mutate(item.id)
                        }
                      }}
                      aria-label={`${item.title} sil`}
                    >
                      <Trash2 size={16} />
                    </Button>
                  ) : null}
                </Card>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
