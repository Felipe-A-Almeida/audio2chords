import { ref, computed, onUnmounted } from 'vue'

export function usePlayback() {
  const audioEl     = ref(null)
  const isPlaying   = ref(false)
  const currentTime = ref(0)
  const duration    = ref(0)
  const chords      = ref([])

  // ── Sticky chord index ─────────────────────────────────────────────────
  // Same logic as ChordViewer — never returns -1 while playing.
  // Holds the last known chord when currentTime falls in a gap.
  const currentChordIdx = computed(() => {
    if (!chords.value.length) return -1

    const exact = chords.value.findIndex(
      c => currentTime.value >= c.start_seconds && currentTime.value < c.end_seconds
    )
    if (exact !== -1) return exact
    if (currentTime.value < chords.value[0].start_seconds) return 0

    let lastStarted = 0
    for (let i = 0; i < chords.value.length; i++) {
      if (chords.value[i].start_seconds <= currentTime.value) lastStarted = i
      else break
    }
    return lastStarted
  })

  const currentChord = computed(() =>
    currentChordIdx.value >= 0 ? chords.value[currentChordIdx.value] : null
  )

  const progress = computed(() =>
    duration.value > 0 ? currentTime.value / duration.value : 0
  )

  function onTimeUpdate()     { currentTime.value = audioEl.value?.currentTime ?? 0 }
  function onDurationChange() { duration.value    = audioEl.value?.duration    ?? 0 }
  function onPlay()           { isPlaying.value   = true  }
  function onPause()          { isPlaying.value   = false }
  function onEnded()          { isPlaying.value   = false }

  function attachElement(el) {
    audioEl.value = el
    el.addEventListener('timeupdate',     onTimeUpdate)
    el.addEventListener('durationchange', onDurationChange)
    el.addEventListener('play',           onPlay)
    el.addEventListener('pause',          onPause)
    el.addEventListener('ended',          onEnded)
  }

  function detachElement() {
    const el = audioEl.value
    if (!el) return
    el.removeEventListener('timeupdate',     onTimeUpdate)
    el.removeEventListener('durationchange', onDurationChange)
    el.removeEventListener('play',           onPlay)
    el.removeEventListener('pause',          onPause)
    el.removeEventListener('ended',          onEnded)
  }

  function toggle() {
    const el = audioEl.value
    if (!el) return
    isPlaying.value ? el.pause() : el.play()
  }

  function seek(seconds) {
    if (audioEl.value) audioEl.value.currentTime = seconds
  }

  function setChords(chordList) {
    chords.value = chordList
  }

  onUnmounted(detachElement)

  return {
    audioEl, isPlaying, currentTime, duration,
    progress, currentChord,
    toggle, seek, setChords,
    attachElement, detachElement,
  }
}
