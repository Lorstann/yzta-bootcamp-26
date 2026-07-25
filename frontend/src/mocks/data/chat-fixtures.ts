/** Fixture payloads for MSW chat stream mock. */

export const MOCK_CHAT_CHUNKS = [
  'Merhaba, ',
  'bu hafta nasıl ',
  'gidiyor? ',
  'Birlikte kısa bir plan çıkaralım.',
] as const

export const MOCK_WEEKLY_TASKS = [
  'Müfredattan 1 modül tekrarı yap',
  'Kısa bir LinkedIn profil gözden geçirmesi',
  'Mentöre 1 soru hazırla',
] as const

export function encodeSse(payload: unknown): string {
  return `data: ${JSON.stringify(payload)}\n\n`
}
