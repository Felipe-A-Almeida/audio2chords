/**
 * usePlayback — manages audio playback state and chord synchronization.
 *
 * Uses HTMLAudioElement (not WaveSurfer) for the timing source so we
 * have a single authoritative currentTime. WaveSurfer is used only
 * for rendering the interactive waveform with a playhead cursor.
 *
 * Returns:
 *   - audioEl      : ref to the HTMLAudioElement (attach to <audio> tag)
 *   - isPlaying    : computed boolean
 *   - currentTime  : reactive seconds
 *   - duration     : reactive seconds
 *   - currentChord : the ChordEvent active at currentTime (or null)
 *   - toggle()     : play / pause
 *   - seek(t)      : jump to time in seconds
 *   - setChords()  : load chord timeline
 */
import { ref, computed, onUnmounted } from 'vue'

export function usePlayback() {
  const audioEl     = ref(null)   // bound to <audio> element in template
  const isPlaying   = ref(false)
  const currentTime = ref(0)
  const duration    = ref(0)
  const chords      = ref([])

  // The chord whose [start, end) window contains currentTime
  const currentChord = computed(() => {
    if (!chords.value.length) return null
    return chords.value.find(
      c => currentTime.value >= c.start_seconds && currentTime.value < c.end_seconds
    ) ?? null
  })

  // Progress 0–1 for a custom progress bar
  const progress = computed(() =>
    duration.value > 0 ? currentTime.value / duration.value : 0
  )

  // ── Event handlers wired to the <audio> element ────────────────────────
  function onTimeUpdate() {
    currentTime.value = audioEl.value?.currentTime ?? 0
  }
  function onDurationChange() {
    duration.value = audioEl.value?.duration ?? 0
  }
  function onPlay()  { isPlaying.value = true  }
  function onPause() { isPlaying.value = false }
  function onEnded() { isPlaying.value = false }

  function attachElement(el) {
    audioEl.value = el
    el.addEventListener('timeupdate',      onTimeUpdate)
    el.addEventListener('durationchange',  onDurationChange)
    el.addEventListener('play',            onPlay)
    el.addEventListener('pause',           onPause)
    el.addEventListener('ended',           onEnded)
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

  // ── Controls ────────────────────────────────────────────────────────────
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
    audioEl,
    isPlaying,
    currentTime,
    duration,
    progress,
    currentChord,
    toggle,
    seek,
    setChords,
    attachElement,
    detachElement,
  }
}
