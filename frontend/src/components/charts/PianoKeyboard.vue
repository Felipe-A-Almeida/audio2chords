<script setup>
/**
 * PianoKeyboard — renders a 2-octave SVG piano keyboard (C3–B4)
 * and highlights the keys that belong to the current chord.
 *
 * Props:
 *   midiNotes : number[]  — MIDI note numbers to highlight (e.g. [60, 64, 67] for C major)
 *   label     : string    — chord name displayed below the keyboard
 */
import { computed } from 'vue'

const props = defineProps({
  midiNotes: { type: Array, default: () => [] },
  label:     { type: String, default: '' },
})

// ── Layout constants ─────────────────────────────────────────────────────
const WHITE_W  = 28   // white key width
const WHITE_H  = 100  // white key height
const BLACK_W  = 18   // black key width
const BLACK_H  = 62   // black key height
const OCTAVES  = 2    // C3–B4
const START_OCTAVE = 3

// White key note offsets within octave: C D E F G A B
const WHITE_OFFSETS = [0, 2, 4, 5, 7, 9, 11]
// Black key note offsets: C# D# — F# G# A#
const BLACK_OFFSETS = [1, 3, -1, 6, 8, 10, -1]  // -1 = no black key after E and B

// ── Build key list ───────────────────────────────────────────────────────
const keys = computed(() => {
  const whites = []
  const blacks = []

  for (let oct = 0; oct < OCTAVES; oct++) {
    const baseNote = (START_OCTAVE + oct) * 12  // MIDI note for C of this octave

    WHITE_OFFSETS.forEach((offset, i) => {
      const midi = baseNote + offset
      // Normalise to pitch class (0–11) for matching voicings that span octaves
      const active = props.midiNotes.some(n => n % 12 === midi % 12)
      whites.push({
        midi, active,
        x: (oct * 7 + i) * WHITE_W,
        y: 0,
        w: WHITE_W - 1,
        h: WHITE_H,
      })
    })

    BLACK_OFFSETS.forEach((offset, i) => {
      if (offset === -1) return   // no black key here (E→F, B→C gaps)
      const midi  = baseNote + offset
      const active = props.midiNotes.some(n => n % 12 === midi % 12)
      // Black key x: sits between white keys i and i+1
      const whiteX = (oct * 7 + i) * WHITE_W
      blacks.push({
        midi, active,
        x: whiteX + WHITE_W - BLACK_W / 2,
        y: 0,
        w: BLACK_W,
        h: BLACK_H,
      })
    })
  }
  return { whites, blacks }
})

const svgWidth  = computed(() => OCTAVES * 7 * WHITE_W)
const svgHeight = WHITE_H + 28   // keyboard + label area
</script>

<template>
  <div class="flex flex-col items-center gap-2">
    <svg
      :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
      :width="svgWidth"
      :height="svgHeight"
      class="w-full max-w-xs"
    >
      <!-- White keys (drawn first so black keys overlap correctly) -->
      <rect
        v-for="(k, i) in keys.whites" :key="'w'+i"
        :x="k.x" :y="k.y" :width="k.w" :height="k.h"
        :fill="k.active ? '#7C3AED' : '#F1F0FF'"
        :stroke="'#1E1E2E'"
        stroke-width="1"
        rx="2"
        class="transition-colors duration-200"
      />

      <!-- Black keys -->
      <rect
        v-for="(k, i) in keys.blacks" :key="'b'+i"
        :x="k.x" :y="k.y" :width="k.w" :height="k.h"
        :fill="k.active ? '#A78BFA' : '#12121A'"
        :stroke="'#0A0A0F'"
        stroke-width="1"
        rx="2"
        class="transition-colors duration-200"
      />

      <!-- Chord label -->
      <text
        :x="svgWidth / 2"
        :y="WHITE_H + 20"
        text-anchor="middle"
        font-family="Syne, sans-serif"
        font-weight="700"
        font-size="14"
        :fill="label ? '#7C3AED' : '#6B7280'"
      >
        {{ label || '—' }}
      </text>
    </svg>
  </div>
</template>
