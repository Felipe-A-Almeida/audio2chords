<script setup>
import { computed } from 'vue'
import { formatTimestamp } from '@/utils/formatters'

const props = defineProps({
  chords:       { type: Array,  required: true },
  duration:     { type: Number, required: true },
  currentTime:  { type: Number, default: 0 },     // from usePlayback
  onSeek:       { type: Function, default: null }, // seek callback
})

const CHORD_COLORS = {
  C: '#7C3AED', D: '#2563EB', E: '#059669', F: '#D97706',
  G: '#DC2626', A: '#7C3AED', B: '#0891B2', '?': '#374151',
}

function colorFor(chord) {
  const root = chord.replace(/[^A-G#b]/g, '').charAt(0) || '?'
  return CHORD_COLORS[root] ?? '#374151'
}

const segments = computed(() =>
  props.chords.map(c => ({
    ...c,
    widthPct: ((c.end_seconds - c.start_seconds) / props.duration) * 100,
    color: colorFor(c.chord),
    active: props.currentTime >= c.start_seconds && props.currentTime < c.end_seconds,
  }))
)

// Playhead position as % across the timeline bar
const playheadPct = computed(() =>
  props.duration > 0 ? (props.currentTime / props.duration) * 100 : 0
)

function handleSegmentClick(seg) {
  if (props.onSeek) props.onSeek(seg.start_seconds)
}
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">Chord Progression</h3>

    <!-- Timeline bar with playhead -->
    <div class="relative">
      <div class="flex h-10 rounded-xl overflow-hidden gap-px mb-1">
        <div
          v-for="(seg, i) in segments" :key="i"
          class="flex items-center justify-center text-white text-xs font-mono
                 font-semibold truncate px-1 transition-all duration-200 cursor-pointer"
          :class="seg.active ? 'brightness-125 ring-2 ring-white/30' : 'opacity-80 hover:opacity-100'"
          :style="{ width: `${seg.widthPct}%`, background: seg.color }"
          :title="`${seg.chord} — ${formatTimestamp(seg.start_seconds)}`"
          @click="handleSegmentClick(seg)"
        >
          {{ seg.widthPct > 4 ? seg.chord : '' }}
        </div>
      </div>

      <!-- Playhead indicator -->
      <div
        class="absolute top-0 h-10 w-0.5 bg-white/80 rounded-full pointer-events-none
               transition-all duration-100"
        :style="{ left: `${playheadPct}%` }"
      />
    </div>

    <!-- Current chord highlight -->
    <div v-if="currentTime > 0" class="mt-3 flex items-center gap-3 py-2 px-3
         bg-chord-surface/80 rounded-lg border border-chord-border/60">
      <div class="w-2 h-2 rounded-full animate-pulse"
           :style="{ background: segments.find(s => s.active)?.color ?? '#374151' }"></div>
      <span class="font-mono text-xs text-chord-muted">Now playing</span>
      <span class="font-display font-bold text-chord-accent text-lg ml-auto">
        {{ segments.find(s => s.active)?.chord ?? '—' }}
      </span>
    </div>

    <!-- Text list — clickable to seek -->
    <div class="space-y-1 max-h-48 overflow-y-auto pr-1 mt-4">
      <div
        v-for="(seg, i) in segments" :key="i"
        class="flex items-center gap-3 py-1.5 border-b border-chord-border/40
               last:border-0 cursor-pointer rounded-lg px-2 transition-colors"
        :class="seg.active
          ? 'bg-chord-accent/10 border-chord-accent/20'
          : 'hover:bg-chord-surface/60'"
        @click="handleSegmentClick(seg)"
      >
        <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: seg.color }"></div>
        <span class="font-mono text-xs text-chord-muted w-12 shrink-0">
          {{ formatTimestamp(seg.start_seconds) }}
        </span>
        <span class="font-display font-semibold text-sm"
              :class="seg.active ? 'text-chord-accent' : 'text-chord-text'">
          {{ seg.chord }}
        </span>
        <span class="ml-auto text-chord-muted text-xs font-mono">
          {{ (seg.confidence * 100).toFixed(0) }}%
        </span>
      </div>
    </div>
  </div>
</template>
