<script setup>
import { computed } from 'vue'
import voicings      from '@/assets/voicings.json'
import PianoKeyboard from './PianoKeyboard.vue'
import GuitarDiagram from './GuitarDiagram.vue'

const props = defineProps({
  chords:      { type: Array,  default: () => [] },
  currentTime: { type: Number, default: 0 },
})

// ── Sticky index ───────────────────────────────────────────────────────────
// Never returns -1 while the track has started.
// Falls back to the most recently started chord when currentTime falls in a
// gap between segments (transient silence, merge boundary, end of track).
const currentIdx = computed(() => {
  if (!props.chords.length) return -1

  // Exact match — currentTime is within a chord window
  const exact = props.chords.findIndex(
    c => props.currentTime >= c.start_seconds && props.currentTime < c.end_seconds
  )
  if (exact !== -1) return exact

  // Before first chord — show the first one as "coming up"
  if (props.currentTime < props.chords[0].start_seconds) return 0

  // Gap or past the end — hold the last chord that already started
  let lastStarted = 0
  for (let i = 0; i < props.chords.length; i++) {
    if (props.chords[i].start_seconds <= props.currentTime) lastStarted = i
    else break
  }
  return lastStarted
})

const prevChord    = computed(() => props.chords[currentIdx.value - 1] ?? null)
const currentChord = computed(() => props.chords[currentIdx.value] ?? null)
const nextChord    = computed(() => props.chords[currentIdx.value + 1] ?? null)

function voicingFor(ev) {
  return ev ? (voicings[ev.chord] ?? null) : null
}

const isPlaying = computed(() => props.currentTime > 0)

// Is currentTime exactly inside the current chord window?
const isExactMatch = computed(() => {
  const c = currentChord.value
  return !!c && props.currentTime >= c.start_seconds && props.currentTime < c.end_seconds
})

// Progress bar within current chord (full bar when in gap/sticky)
const segmentProgress = computed(() => {
  const c = currentChord.value
  if (!c || !isExactMatch.value) return 100
  return Math.min(100,
    ((props.currentTime - c.start_seconds) / (c.end_seconds - c.start_seconds)) * 100
  )
})
</script>

<template>
  <div class="card overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="label">Chord Diagrams</h3>
      <div v-if="currentChord && isPlaying" class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-chord-accent"
              :class="isExactMatch ? 'animate-pulse' : 'opacity-40'"></span>
        <span class="font-mono text-xs text-chord-muted">
          {{ isExactMatch ? 'live' : 'last chord' }}
        </span>
      </div>
      <span v-else class="label">press play</span>
    </div>

    <!-- ═══════════════════════════════════════════════════
         DESKTOP (md+): three columns
         ═══════════════════════════════════════════════ -->
    <div class="hidden md:grid grid-cols-3 gap-4 items-start">

      <!-- Previous -->
      <div class="flex flex-col items-center gap-3 transition-opacity duration-500"
           :class="prevChord ? 'opacity-35' : 'opacity-0'">
        <div class="text-center">
          <p class="label mb-1">Previous</p>
          <p class="font-display font-bold text-2xl text-chord-muted">
            {{ prevChord?.chord ?? '·' }}
          </p>
        </div>
        <template v-if="prevChord && voicingFor(prevChord)">
          <div class="flex gap-4 justify-center flex-wrap">
            <PianoKeyboard :midiNotes="voicingFor(prevChord).piano" label="" />
            <GuitarDiagram :frets="voicingFor(prevChord).guitar"
                           :barre="voicingFor(prevChord).barre" label="" />
          </div>
        </template>
      </div>

      <!-- Current -->
      <div class="flex flex-col items-center gap-4 relative">
        <div class="absolute inset-0 bg-chord-accent/5 rounded-2xl blur-xl pointer-events-none"></div>
        <div class="text-center relative z-10">
          <p class="label mb-1">Now</p>
          <p class="font-display font-extrabold text-5xl tracking-tight"
             :class="currentChord ? 'text-chord-accent' : 'text-chord-border'">
            {{ currentChord?.chord ?? '—' }}
          </p>
          <p v-if="currentChord" class="font-mono text-xs text-chord-muted mt-1">
            {{ (currentChord.confidence * 100).toFixed(0) }}% confidence
          </p>
        </div>
        <template v-if="currentChord && voicingFor(currentChord)">
          <div class="flex gap-6 justify-center flex-wrap relative z-10">
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Piano</span>
              <PianoKeyboard :midiNotes="voicingFor(currentChord).piano"
                             :label="currentChord.chord" />
            </div>
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Guitar</span>
              <GuitarDiagram :frets="voicingFor(currentChord).guitar"
                             :barre="voicingFor(currentChord).barre"
                             :label="currentChord.chord" />
            </div>
          </div>
        </template>
        <div v-else-if="currentChord"
             class="flex flex-col items-center gap-1 text-chord-muted py-4 relative z-10">
          <span class="text-2xl">🎵</span>
          <p class="font-mono text-xs">no diagram available</p>
        </div>
        <!-- Only show "press play" if playback truly hasn't started -->
        <div v-else class="flex flex-col items-center gap-2 py-6 text-chord-muted">
          <span class="text-3xl">▶</span>
          <p class="font-mono text-xs">press play</p>
        </div>
      </div>

      <!-- Next -->
      <div class="flex flex-col items-center gap-3 transition-opacity duration-500"
           :class="nextChord ? 'opacity-35' : 'opacity-0'">
        <div class="text-center">
          <p class="label mb-1">Next</p>
          <p class="font-display font-bold text-2xl text-chord-muted">
            {{ nextChord?.chord ?? '·' }}
          </p>
        </div>
        <template v-if="nextChord && voicingFor(nextChord)">
          <div class="flex gap-4 justify-center flex-wrap">
            <PianoKeyboard :midiNotes="voicingFor(nextChord).piano" label="" />
            <GuitarDiagram :frets="voicingFor(nextChord).guitar"
                           :barre="voicingFor(nextChord).barre" label="" />
          </div>
        </template>
      </div>
    </div>

    <!-- ═══════════════════════════════════════════════════
         MOBILE (< md): stacked
         ═══════════════════════════════════════════════ -->
    <div class="md:hidden flex flex-col items-center gap-4">

      <!-- Previous — name only -->
      <div class="flex items-center gap-2 transition-opacity duration-500"
           :class="prevChord ? 'opacity-40' : 'opacity-0'">
        <span class="font-mono text-xs text-chord-muted">prev</span>
        <span class="font-display font-bold text-lg text-chord-muted">
          {{ prevChord?.chord ?? '·' }}
        </span>
      </div>

      <!-- Current — hero -->
      <div class="w-full flex flex-col items-center gap-4 relative py-2">
        <div class="absolute inset-0 bg-chord-accent/5 rounded-2xl blur-xl pointer-events-none"></div>
        <div class="text-center relative z-10">
          <p class="font-display font-extrabold text-6xl tracking-tight"
             :class="currentChord ? 'text-chord-accent' : 'text-chord-border'">
            {{ currentChord?.chord ?? '—' }}
          </p>
          <p v-if="currentChord" class="font-mono text-xs text-chord-muted mt-1">
            {{ (currentChord.confidence * 100).toFixed(0) }}% confidence
          </p>
        </div>
        <template v-if="currentChord && voicingFor(currentChord)">
          <div class="flex gap-8 justify-center flex-wrap relative z-10">
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Piano</span>
              <PianoKeyboard :midiNotes="voicingFor(currentChord).piano"
                             :label="currentChord.chord" />
            </div>
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Guitar</span>
              <GuitarDiagram :frets="voicingFor(currentChord).guitar"
                             :barre="voicingFor(currentChord).barre"
                             :label="currentChord.chord" />
            </div>
          </div>
        </template>
        <div v-else class="py-6 text-chord-muted">
          <p class="font-mono text-xs text-center">press play</p>
        </div>
      </div>

      <!-- Next — name only -->
      <div class="flex items-center gap-2 transition-opacity duration-500"
           :class="nextChord ? 'opacity-40' : 'opacity-0'">
        <span class="font-mono text-xs text-chord-muted">next</span>
        <span class="font-display font-bold text-lg text-chord-muted">
          {{ nextChord?.chord ?? '·' }}
        </span>
      </div>
    </div>

    <!-- Progress bar -->
    <div v-if="currentChord && isPlaying" class="mt-6">
      <div class="h-0.5 bg-chord-border rounded-full overflow-hidden">
        <div class="h-full rounded-full transition-all duration-100"
             :class="isExactMatch ? 'bg-chord-accent/60' : 'bg-chord-muted/30'"
             :style="{ width: `${segmentProgress}%` }" />
      </div>
    </div>

  </div>
</template>
