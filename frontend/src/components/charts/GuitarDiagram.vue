<script setup>
/**
 * GuitarDiagram — renders a guitar fretboard diagram (chord grid) as SVG.
 *
 * Standard chord diagram format:
 *   - 6 vertical lines = strings (low E left, high E right)
 *   - 5 horizontal lines = frets
 *   - Filled circles = finger positions
 *   - × above string = muted
 *   - O above string = open
 *   - Barre bar = flat finger across all strings at a fret
 *
 * Props:
 *   frets  : number[6] — fret positions per string, -1 = muted, 0 = open
 *   barre  : number|null — fret number where barre occurs (null = no barre)
 *   label  : string — chord name
 */
import { computed } from 'vue'

const props = defineProps({
  frets: { type: Array,  default: () => [-1,-1,-1,-1,-1,-1] },
  barre: { type: Number, default: null },
  label: { type: String, default: '' },
})

// ── Layout ───────────────────────────────────────────────────────────────
const STRING_GAP = 28   // horizontal distance between strings
const FRET_GAP   = 24   // vertical distance between frets
const STRINGS    = 6
const FRETS      = 5
const PAD_TOP    = 36   // space for open/mute indicators + nut
const PAD_LEFT   = 20
const DOT_R      = 9    // finger dot radius

const GRID_W = (STRINGS - 1) * STRING_GAP
const GRID_H = FRETS * FRET_GAP
const SVG_W  = GRID_W + PAD_LEFT * 2
const SVG_H  = GRID_H + PAD_TOP + 30   // 30 = label area

// ── Derived positions ────────────────────────────────────────────────────
// Find the minimum fret to show (for high-position chords)
const minFret = computed(() => {
  const played = props.frets.filter(f => f > 0)
  if (!played.length) return 1
  const m = Math.min(...played)
  return m <= 2 ? 1 : m
})

const showNut = computed(() => minFret.value === 1)

// Convert a fret number to Y coordinate on the diagram
function fretY(fret) {
  return PAD_TOP + (fret - minFret.value + 0.5) * FRET_GAP
}

// String X coordinate (string 0 = low E, leftmost)
function stringX(s) {
  return PAD_LEFT + s * STRING_GAP
}

// Dots: one per string that is fretted (not muted, not open)
const dots = computed(() =>
  props.frets
    .map((fret, s) => ({ fret, s, x: stringX(s), y: fretY(fret) }))
    .filter(d => d.fret > 0)
)

// Barre bar SVG rect
const barreBar = computed(() => {
  if (!props.barre) return null
  return {
    x1: PAD_LEFT,
    x2: PAD_LEFT + GRID_W,
    y:  fretY(props.barre),
  }
})
</script>

<template>
  <div class="flex flex-col items-center gap-2">
    <svg
      :viewBox="`0 0 ${SVG_W} ${SVG_H}`"
      :width="SVG_W"
      :height="SVG_H"
      class="w-full max-w-[180px]"
    >
      <!-- Nut (thick top bar if in open position) -->
      <rect
        v-if="showNut"
        :x="PAD_LEFT - 2" :y="PAD_TOP - 4"
        :width="GRID_W + 4" height="5"
        fill="#F1F0FF" rx="1"
      />

      <!-- Fret lines -->
      <line
        v-for="f in FRETS + 1" :key="'f'+f"
        :x1="PAD_LEFT" :y1="PAD_TOP + (f-1) * FRET_GAP"
        :x2="PAD_LEFT + GRID_W" :y2="PAD_TOP + (f-1) * FRET_GAP"
        stroke="#2D2D3F" stroke-width="1"
      />

      <!-- String lines -->
      <line
        v-for="s in STRINGS" :key="'s'+s"
        :x1="PAD_LEFT + (s-1) * STRING_GAP" :y1="PAD_TOP"
        :x2="PAD_LEFT + (s-1) * STRING_GAP" :y2="PAD_TOP + GRID_H"
        stroke="#4B4B6B" stroke-width="1.5"
      />

      <!-- Mute / Open indicators above strings -->
      <g v-for="(fret, s) in frets" :key="'ind'+s">
        <!-- × muted -->
        <text
          v-if="fret === -1"
          :x="stringX(s)" :y="PAD_TOP - 14"
          text-anchor="middle"
          font-size="13"
          font-family="JetBrains Mono, monospace"
          fill="#6B7280"
        >×</text>
        <!-- O open -->
        <circle
          v-else-if="fret === 0"
          :cx="stringX(s)" :cy="PAD_TOP - 14"
          r="5"
          fill="none" stroke="#6B7280" stroke-width="1.5"
        />
      </g>

      <!-- Barre bar -->
      <rect
        v-if="barreBar"
        :x="barreBar.x1"
        :y="barreBar.y - DOT_R"
        :width="barreBar.x2 - barreBar.x1"
        :height="DOT_R * 2"
        fill="#7C3AED"
        rx="9"
        opacity="0.9"
      />

      <!-- Finger dots -->
      <circle
        v-for="(dot, i) in dots" :key="'d'+i"
        :cx="dot.x" :cy="dot.y"
        :r="DOT_R"
        fill="#7C3AED"
      />

      <!-- Position number (for high fret chords) -->
      <text
        v-if="!showNut && minFret > 1"
        :x="PAD_LEFT + GRID_W + 8"
        :y="PAD_TOP + FRET_GAP * 0.5 + 4"
        font-size="10"
        font-family="JetBrains Mono, monospace"
        fill="#6B7280"
      >{{ minFret }}fr</text>

      <!-- Chord label -->
      <text
        :x="SVG_W / 2"
        :y="SVG_H - 8"
        text-anchor="middle"
        font-family="Syne, sans-serif"
        font-weight="700"
        font-size="14"
        :fill="label ? '#7C3AED' : '#6B7280'"
      >{{ label || '—' }}</text>
    </svg>
  </div>
</template>
