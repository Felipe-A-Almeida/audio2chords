<script setup>
/**
 * ChordFilterPanel — chip-based panel to show/hide entire chord groups
 * from the whole analysis (timeline + viewer).
 *
 * Props:
 *   uniqueChords  : string[]   — all chord names present in the track
 *   hiddenChords  : Set        — chord names currently hidden
 *
 * Emits:
 *   toggle(name)  — toggle a chord name
 *   showAll       — make all chords visible
 *   hideAll       — hide all chords
 */
import { computed } from 'vue'

const props = defineProps({
  uniqueChords: { type: Array,  required: true },
  hiddenChords: { type: Object, required: true },   // Set
})

const emit = defineEmits(['toggle', 'showAll', 'hideAll'])

const visibleCount = computed(() =>
  props.uniqueChords.filter(c => !props.hiddenChords.has(c)).length
)

const allVisible  = computed(() => visibleCount.value === props.uniqueChords.length)
const noneVisible = computed(() => visibleCount.value === 0)

// Colour per chord root — same palette as ChordTimeline
const COLORS = {
  C:'#7C3AED', D:'#2563EB', E:'#059669', F:'#D97706',
  G:'#DC2626', A:'#7C3AED', B:'#0891B2',
}
function colorFor(chord) {
  const root = chord.replace(/[^A-G#b]/g,'').charAt(0) || '?'
  return COLORS[root] ?? '#374151'
}
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <h3 class="label">Chord Groups</h3>
      <div class="flex gap-2">
        <button
          @click="emit('showAll')"
          :disabled="allVisible"
          class="text-xs font-mono px-3 py-1 rounded-lg border transition-colors
                 disabled:opacity-30 disabled:cursor-not-allowed
                 border-chord-border text-chord-muted hover:border-chord-accent/50
                 hover:text-chord-accent"
        >Show all</button>
        <button
          @click="emit('hideAll')"
          :disabled="noneVisible"
          class="text-xs font-mono px-3 py-1 rounded-lg border transition-colors
                 disabled:opacity-30 disabled:cursor-not-allowed
                 border-chord-border text-chord-muted hover:border-red-500/50
                 hover:text-red-400"
        >Hide all</button>
      </div>
    </div>

    <!-- Chord chips -->
    <div class="flex flex-wrap gap-2">
      <button
        v-for="chord in uniqueChords" :key="chord"
        @click="emit('toggle', chord)"
        class="flex items-center gap-2 px-3 py-1.5 rounded-xl border text-sm
               font-mono font-semibold transition-all duration-200"
        :class="hiddenChords.has(chord)
          ? 'opacity-35 border-chord-border bg-chord-surface text-chord-muted'
          : 'border-transparent text-white'"
        :style="!hiddenChords.has(chord)
          ? { background: colorFor(chord) }
          : {}"
      >
        <!-- Checkbox indicator -->
        <span class="w-3.5 h-3.5 rounded border flex items-center justify-center shrink-0 transition-colors"
              :class="hiddenChords.has(chord)
                ? 'border-chord-muted'
                : 'border-white/60 bg-white/20'">
          <svg v-if="!hiddenChords.has(chord)" class="w-2.5 h-2.5 text-white"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
          </svg>
        </span>
        {{ chord }}
      </button>
    </div>

    <!-- Summary -->
    <p class="mt-3 text-xs font-mono text-chord-muted">
      {{ visibleCount }} of {{ uniqueChords.length }} chord types visible
    </p>
  </div>
</template>
