/** Fixture payloads for MSW chat stream mock. */

export const MOCK_CHAT_CHUNKS = [
  'Merhaba, ',
  'bugün nasıl ',
  'gidiyor? ',
  'Birlikte kısa bir plan çıkaralım.',
] as const

export const MOCK_DAILY_TASKS = [
  {
    title: 'Pandas groupby tekrarı',
    description: 'Tek dataset üzerinde 3 agregasyon yaz, 30 dk, notebook’a kaydet',
  },
  {
    title: 'Bornova’da kısa yürüyüş',
    description: '20–30 dk açık havada yürü, telefonu sessize al',
  },
  {
    title: 'SQL JOIN örneği',
    description: 'İki tabloyu LEFT JOIN ile birleştirip 5 satır sonuç al',
  },
] as const

export function encodeSse(payload: unknown): string {
  return `data: ${JSON.stringify(payload)}\n\n`
}
