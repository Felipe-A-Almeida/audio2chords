<script setup>
import { computed } from 'vue'
import { formatTimestamp } from '@/utils/formatters'

const props = defineProps({
  chords:   { type: Array, required: true },   // ChordEvent[]
  duration: { type: Number, required: true },
})

// Map chord root to a colour for visual variety
const CHORD_COLORS = {
  C: '#7C3AED', D: '#2563EB', E: '#059669', F: '#D97706',
  G: '#DC2626', A: '#7C3AED', B: '#0891B2',
  '?': '#374151',
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
  }))
)
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">Chord Progression</h3>

    <!-- Visual timeline bar -->
    <div class="flex h-10 rounded-xl overflow-hidden gap-px mb-4">
      <div
        v-for="(seg, i) in segments" :key="i"
        class="flex items-center justify-center text-white text-xs font-mono
               font-semibold truncate px-1 transition-all hover:brightness-110
               cursor-default"
        :style="{ width: `${seg.widthPct}%`, background: seg.color }"
        :title="`${seg.chord} — ${formatTimestamp(seg.start_seconds)}`"
      >
        {{ seg.widthPct > 4 ? seg.chord : '' }}
      </div>
    </div>

    <!-- Text list -->
    <div class="space-y-1 max-h-48 overflow-y-auto pr-1">
      <div
        v-for="(seg, i) in segments" :key="i"
        class="flex items-center gap-3 py-1.5 border-b border-chord-border/40 last:border-0"
      >
        <div class="w-2 h-2 rounded-full shrink-0" :style="{ background: seg.color }"></div>
        <span class="font-mono text-xs text-chord-muted w-12 shrink-0">
          {{ formatTimestamp(seg.start_seconds) }}
        </span>
        <span class="font-display font-semibold text-sm text-chord-text">
          {{ seg.chord }}
        </span>
        <span class="ml-auto text-chord-muted text-xs font-mono">
          {{ (seg.confidence * 100).toFixed(0) }}%
        </span>
      </div>
    </div>
  </div>
</template>
