/** Word-scale labels mirrored from backend/services/checkin_flow.py */

export const ENERGY_CHOICES = [
  { label: 'Tükendim', score: 2 },
  { label: 'Yorgunum', score: 4 },
  { label: 'İdare eder', score: 6 },
  { label: 'İyiyim', score: 8 },
  { label: 'Turbo moddayım', score: 10 },
] as const

export const MOTIVATION_CHOICES = [
  { label: 'Hiç yok', score: 2 },
  { label: 'Zorlanıyorum', score: 4 },
  { label: 'Fena değil', score: 6 },
  { label: 'İstekliyim', score: 8 },
  { label: 'Ateşliyim', score: 10 },
] as const

function nearestLabel(
  choices: ReadonlyArray<{ label: string; score: number }>,
  value: number,
): string {
  let best = choices[0]
  for (const c of choices) {
    if (Math.abs(c.score - value) < Math.abs(best.score - value)) {
      best = c
    }
  }
  return best.label
}

export function energyLabel(score: number | null | undefined): string | null {
  if (score == null) return null
  return nearestLabel(ENERGY_CHOICES, score)
}

export function motivationLabel(
  score: number | null | undefined,
): string | null {
  if (score == null) return null
  return nearestLabel(MOTIVATION_CHOICES, score)
}
