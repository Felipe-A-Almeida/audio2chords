<script setup>
/**
 * ChordViewer v2 — full-width row showing prev / current / next chord.
 *
 * Props:
 *   chords      : ChordEvent[]  — full chord timeline
 *   currentTime : number        — playback position in seconds
 */
import { computed } from 'vue'
import voicings      from '@/assets/voicings.json'
import PianoKeyboard from './PianoKeyboard.vue'
import GuitarDiagram from './GuitarDiagram.vue'

const props = defineProps({
  chords:      { type: Array,  default: () => [] },
  currentTime: { type: Number, default: 0 },
})

// Index of the chord currently playing
const currentIdx = computed(() => {
  if (!props.chords.length) return -1
  const idx = props.chords.findIndex(
    c => props.currentTime >= c.start_seconds && props.currentTime < c.end_seconds
  )
  // Before first chord starts — show first chord as "current"
  if (idx === -1 && props.currentTime < props.chords[0]?.start_seconds) return 0
  return idx
})

const prevChord    = computed(() => props.chords[currentIdx.value - 1] ?? null)
const currentChord = computed(() => props.chords[currentIdx.value] ?? null)
const nextChord    = computed(() => props.chords[currentIdx.value + 1] ?? null)

function voicingFor(chordEvent) {
  if (!chordEvent) return null
  return voicings[chordEvent.chord] ?? null
}

const isPlaying = computed(() => props.currentTime > 0)
</script>

<template>
  <div class="card overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="label">Chord Diagrams</h3>
      <div v-if="currentChord && isPlaying"
           class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-chord-accent animate-pulse"></span>
        <span class="font-mono text-xs text-chord-muted">live</span>
      </div>
      <span v-else class="label">press play</span>
    </div>

    <!-- Three-panel layout: prev · current · next -->
    <div class="grid grid-cols-3 gap-4 items-start">

      <!-- ── PREVIOUS ── -->
      <div class="flex flex-col items-center gap-4 opacity-35 transition-opacity duration-500"
           :class="{ 'opacity-0': !prevChord }">
        <div class="text-center">
          <p class="label mb-1">Previous</p>
          <p class="font-display font-bold text-2xl text-chord-muted">
            {{ prevChord?.chord ?? '·' }}
          </p>
        </div>
        <template v-if="prevChord && voicingFor(prevChord)">
          <div class="flex gap-6 justify-center flex-wrap">
            <PianoKeyboard
              :midiNotes="voicingFor(prevChord).piano"
              :label="''"
            />
            <GuitarDiagram
              :frets="voicingFor(prevChord).guitar"
              :barre="voicingFor(prevChord).barre"
              :label="''"
            />
          </div>
        </template>
        <div v-else class="h-24 flex items-center">
          <span class="text-chord-border text-4xl font-display">—</span>
        </div>
      </div>

      <!-- ── CURRENT (hero) ── -->
      <div class="flex flex-col items-center gap-4 transition-all duration-300
                  relative">
        <!-- Glow behind current chord -->
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
          <div class="flex gap-8 justify-center flex-wrap relative z-10">
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Piano</span>
              <PianoKeyboard
                :midiNotes="voicingFor(currentChord).piano"
                :label="currentChord.chord"
              />
            </div>
            <div class="flex flex-col items-center gap-1">
              <span class="label text-xs mb-1">Guitar</span>
              <GuitarDiagram
                :frets="voicingFor(currentChord).guitar"
                :barre="voicingFor(currentChord).barre"
                :label="currentChord.chord"
              />
            </div>
          </div>
        </template>

        <!-- No voicing found for this chord -->
        <div v-else-if="currentChord"
             class="flex flex-col items-center gap-1 text-chord-muted py-4 relative z-10">
          <span class="text-2xl">🎵</span>
          <p class="font-mono text-xs">no diagram available</p>
        </div>

        <!-- Not playing yet -->
        <div v-else class="flex flex-col items-center gap-2 py-6 text-chord-muted">
          <span class="text-3xl">▶</span>
          <p class="font-mono text-xs">press play</p>
        </div>
      </div>

      <!-- ── NEXT ── -->
      <div class="flex flex-col items-center gap-4 opacity-35 transition-opacity duration-500"
           :class="{ 'opacity-0': !nextChord }">
        <div class="text-center">
          <p class="label mb-1">Next</p>
          <p class="font-display font-bold text-2xl text-chord-muted">
            {{ nextChord?.chord ?? '·' }}
          </p>
        </div>
        <template v-if="nextChord && voicingFor(nextChord)">
          <div class="flex gap-6 justify-center flex-wrap">
            <PianoKeyboard
              :midiNotes="voicingFor(nextChord).piano"
              :label="''"
            />
            <GuitarDiagram
              :frets="voicingFor(nextChord).guitar"
              :barre="voicingFor(nextChord).barre"
              :label="''"
            />
          </div>
        </template>
        <div v-else class="h-24 flex items-center">
          <span class="text-chord-border text-4xl font-display">—</span>
        </div>
      </div>

    </div>

    <!-- Progress bar within current chord segment -->
    <div v-if="currentChord && isPlaying" class="mt-6">
      <div class="h-0.5 bg-chord-border rounded-full overflow-hidden">
        <div
          class="h-full bg-chord-accent/60 rounded-full transition-all duration-100"
          :style="{
            width: `${Math.min(100, ((currentTime - currentChord.start_seconds) /
              (currentChord.end_seconds - currentChord.start_seconds)) * 100)}%`
          }"
        />
      </div>
    </div>

  </div>
</template>
