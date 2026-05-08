import { computed } from 'vue'

export function useAnalysis(result) {
  const bpmLabel    = computed(() => result.value?.bpm?.bpm?.toFixed(1) ?? '—')
  const keyLabel    = computed(() => result.value?.key?.label ?? '—')
  const duration    = computed(() => result.value?.metadata?.duration_seconds ?? 0)
  const filename    = computed(() => result.value?.metadata?.filename ?? '')
  const chords      = computed(() => result.value?.chords ?? [])
  const waveform    = computed(() => result.value?.waveform?.samples ?? [])
  const spectrogram = computed(() => result.value?.spectrogram ?? null)
  const analysisId  = computed(() => result.value?.analysis_id ?? null)

  // v0.4.1: beat grid data
  const beatTimes     = computed(() => result.value?.bpm?.beat_times ?? [])
  const downbeatTimes = computed(() => result.value?.bpm?.downbeat_times ?? [])

  const audioUrl = computed(() =>
    analysisId.value ? `/api/audio/${analysisId.value}` : null
  )

  function exportJson() {
    if (!result.value) return
    const blob = new Blob([JSON.stringify(result.value, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a   = document.createElement('a')
    a.href     = url
    a.download = `audiochord_${result.value.metadata.filename}.json`
    a.click()
    URL.revokeObjectURL(url)
  }

  return {
    bpmLabel, keyLabel, duration, filename,
    chords, waveform, spectrogram,
    beatTimes, downbeatTimes,
    analysisId, audioUrl,
    exportJson,
  }
}
