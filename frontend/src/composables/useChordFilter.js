/**
 * useChordFilter — manages two independent chord filtering systems:
 *
 * 1. Global filter (hiddenChords): a Set of chord names excluded from the
 *    entire analysis — timeline, viewer, and metrics.
 *
 * 2. Per-event filter (hiddenEvents): a Set of chord event indices
 *    hidden individually from the Chord Progression list only.
 *
 * Both filters compose: a chord event is visible only if its chord name
 * is not in hiddenChords AND its index is not in hiddenEvents.
 */
import { ref, computed } from 'vue'

export function useChordFilter(chords) {
  // Global filter — chord names (e.g. "Am", "F")
  const hiddenChords = ref(new Set())

  // Per-event filter — event indices
  const hiddenEvents = ref(new Set())

  // All unique chord names present in the analysis
  const uniqueChords = computed(() => {
    const seen = new Set()
    const result = []
    for (const c of chords.value) {
      if (!seen.has(c.chord)) {
        seen.add(c.chord)
        result.push(c.chord)
      }
    }
    return result.sort()
  })

  // Toggle a chord name in the global filter
  function toggleChordName(name) {
    const next = new Set(hiddenChords.value)
    next.has(name) ? next.delete(name) : next.add(name)
    hiddenChords.value = next
  }

  // Toggle a single event by index
  function toggleEvent(idx) {
    const next = new Set(hiddenEvents.value)
    next.has(idx) ? next.delete(idx) : next.add(idx)
    hiddenEvents.value = next
  }

  // Select all / clear all chord names
  function showAllChords()  { hiddenChords.value = new Set() }
  function hideAllChords()  { hiddenChords.value = new Set(uniqueChords.value) }

  // Chords visible in the full timeline and viewer
  const globallyVisibleChords = computed(() =>
    chords.value.filter(c => !hiddenChords.value.has(c.chord))
  )

  // Chords visible in the Chord Progression list (applies both filters)
  const progressionVisibleChords = computed(() =>
    chords.value
      .map((c, i) => ({ ...c, _idx: i }))
      .filter(c => !hiddenChords.value.has(c.chord) && !hiddenEvents.value.has(c._idx))
  )

  // Is a specific event visible in the progression list?
  function isEventVisible(idx) {
    return !hiddenEvents.value.has(idx)
  }

  return {
    hiddenChords,
    hiddenEvents,
    uniqueChords,
    toggleChordName,
    toggleEvent,
    showAllChords,
    hideAllChords,
    globallyVisibleChords,
    progressionVisibleChords,
    isEventVisible,
  }
}
