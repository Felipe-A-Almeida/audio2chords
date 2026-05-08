<script setup>
import { computed } from 'vue'
import { formatTimestamp } from '@/utils/formatters'

const props = defineProps({
  chords:        { type: Array,    required: true },
  duration:      { type: Number,   required: true },
  currentTime:   { type: Number,   default: 0 },
  minConfidence: { type: Number,   default: 0 },
  hiddenChords:  { type: Object,   default: () => new Set() },
  hiddenEvents:  { type: Object,   default: () => new Set() },
  onSeek:        { type: Function, default: null },
})

const emit = defineEmits(['toggleEvent'])

const CHORD_COLORS = {
  C:'#7C3AED', D:'#2563EB', E:'#059669', F:'#D97706',
  G:'#DC2626', A:'#7C3AED', B:'#0891B2', '?':'#374151',
}
function colorFor(chord) {
  const root = chord.replace(/[^A-G#b]/g,'').charAt(0) || '?'
  return CHORD_COLORS[root] ?? '#374151'
}

// ── Sticky active index ────────────────────────────────────────────────────
// Same gap-filling logic as ChordViewer so the highlight never disappears
// between chord boundaries.
const activeIdx = computed(() => {
  const list = props.chords
  if (!list.length || props.currentTime <= 0) return -1

  const exact = list.findIndex(
    c => props.currentTime >= c.start_seconds && props.currentTime < c.end_seconds
  )
  if (exact !== -1) return exact
  if (props.currentTime < list[0].start_seconds) return 0

  let last = 0
  for (let i = 0; i < list.length; i++) {
    if (list[i].start_seconds <= props.currentTime) last = i
    else break
  }
  return last
})

// Timeline bar — global filters only (no per-event)
const timelineSegments = computed(() =>
  props.chords
    .map((c, i) => ({ ...c, _idx: i }))
    .filter(c => !props.hiddenChords.has(c.chord) && c.confidence >= props.minConfidence)
    .map((c, _, arr) => ({
      ...c,
      widthPct: ((c.end_seconds - c.start_seconds) / props.duration) * 100,
      color:    colorFor(c.chord),
      active:   c._idx === activeIdx.value,
    }))
)

// List — applies both global and per-event filters
// Shows all events (including hidden ones) so the eye toggle is always visible
const allListSegments = computed(() =>
  props.chords
    .map((c, i) => ({ ...c, _idx: i }))
    .filter(c => !props.hiddenChords.has(c.chord) && c.confidence >= props.minConfidence)
    .map(c => ({
      ...c,
      color:  colorFor(c.chord),
      active: c._idx === activeIdx.value,
      hidden: props.hiddenEvents.has(c._idx),
    }))
)

const playheadPct = computed(() =>
  props.duration > 0 ? (props.currentTime / props.duration) * 100 : 0
)

function handleSeek(seg) {
  if (props.onSeek) props.onSeek(seg.start_seconds)
}

// The currently active chord name for the "now playing" pill
const activeChordName = computed(() => {
  const seg = timelineSegments.value.find(s => s.active)
  return seg?.chord ?? null
})
const activeColor = computed(() => {
  const seg = timelineSegments.value.find(s => s.active)
  return seg?.color ?? '#374151'
})
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">Chord Progression</h3>

    <!-- Timeline bar -->
    <div class="relative mb-1">
      <div class="flex h-8 sm:h-10 rounded-xl overflow-hidden gap-px">
        <div v-for="(seg, i) in timelineSegments" :key="i"
             class="flex items-center justify-center text-white text-xs font-mono
                    font-semibold truncate px-1 transition-all duration-200 cursor-pointer"
             :class="seg.active
               ? 'brightness-125 ring-2 ring-white/30'
               : 'opacity-80 hover:opacity-100'"
             :style="{ width: `${seg.widthPct}%`, background: seg.color }"
             :title="`${seg.chord} — ${formatTimestamp(seg.start_seconds)}`"
             @click="handleSeek(seg)">
          {{ seg.widthPct > 5 ? seg.chord : '' }}
        </div>
      </div>
      <!-- Playhead -->
      <div class="absolute top-0 h-8 sm:h-10 w-0.5 bg-white/80 rounded-full
                  pointer-events-none transition-all duration-100"
           :style="{ left: `${playheadPct}%` }" />
    </div>

    <!-- Now playing pill — only when currentTime > 0 -->
    <div v-if="currentTime > 0 && activeChordName"
         class="mt-3 flex items-center gap-3 py-2 px-3
                bg-chord-surface/80 rounded-lg border border-chord-border/60">
      <div class="w-2 h-2 rounded-full animate-pulse"
           :style="{ background: activeColor }"></div>
      <span class="font-mono text-xs text-chord-muted">Now playing</span>
      <span class="font-display font-bold text-chord-accent text-lg ml-auto">
        {{ activeChordName }}
      </span>
    </div>

    <!-- Event list with eye toggle -->
    <div class="space-y-1 max-h-48 overflow-y-auto pr-1 mt-4">
      <div v-for="seg in allListSegments" :key="seg._idx"
           class="flex items-center gap-2 sm:gap-3 py-1.5 rounded-lg px-2
                  border-b border-chord-border/40 last:border-0 transition-all duration-150"
           :class="[
             seg.active && !seg.hidden ? 'bg-chord-accent/10' : 'hover:bg-chord-surface/60',
             seg.hidden ? 'opacity-40' : ''
           ]">

        <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: seg.color }"></div>

        <span class="font-mono text-xs text-chord-muted w-10 sm:w-12 shrink-0
                     cursor-pointer hover:text-chord-accent transition-colors"
              @click="handleSeek(seg)">
          {{ formatTimestamp(seg.start_seconds) }}
        </span>

        <span class="font-display font-semibold text-sm cursor-pointer
                     hover:text-chord-accent transition-colors flex-1"
              :class="seg.active && !seg.hidden ? 'text-chord-accent' : 'text-chord-text'"
              @click="handleSeek(seg)">
          {{ seg.chord }}
        </span>

        <span class="text-chord-muted text-xs font-mono shrink-0">
          {{ (seg.confidence * 100).toFixed(0) }}%
        </span>

        <!-- Eye toggle -->
        <button @click="emit('toggleEvent', seg._idx)"
                class="shrink-0 p-1 rounded-lg transition-colors hover:bg-chord-border/60"
                :title="seg.hidden ? 'Show this chord' : 'Hide this chord'">
          <!-- Eye open -->
          <svg v-if="!seg.hidden" class="w-4 h-4 text-chord-muted"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5
                     c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639
                     C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
          </svg>
          <!-- Eye closed -->
          <svg v-else class="w-4 h-4 text-chord-muted/40"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12
                     19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112
                     4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0
                     01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894
                     7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243
                     m4.242 4.242L9.88 9.88"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!allListSegments.length" class="py-8 text-center text-chord-muted">
      <p class="font-mono text-sm">No chords match the current filters</p>
    </div>
  </div>
</template>
