<script setup>
/**
 * ConfidenceFilter v2 — chord confidence threshold with:
 *
 *  - Histogram showing distribution of chord confidences
 *  - Smart auto-threshold suggestion (mean − 0.5σ)
 *  - Live preview of how many chords will be kept / removed
 *  - Color-coded threshold zones (low / medium / high)
 *  - Presets with chord count preview on hover
 */
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: { type: Number, default: 0 },   // 0–1
  chords:     { type: Array,  default: () => [] },  // full chord list for stats
})

const emit = defineEmits(['update:modelValue'])

// ── Stats derived from actual chord data ───────────────────────────────────
const confidences = computed(() => props.chords.map(c => c.confidence))

const stats = computed(() => {
  const vals = confidences.value
  if (!vals.length) return { mean: 0, std: 0, auto: 0 }
  const mean = vals.reduce((a, b) => a + b, 0) / vals.length
  const std  = Math.sqrt(vals.reduce((a, b) => a + (b - mean) ** 2, 0) / vals.length)
  const auto = Math.max(0, Math.min(0.9, mean - 0.5 * std))
  return { mean, std, auto }
})

// ── Histogram — 10 buckets across 0–100% ─────────────────────────────────
const histogram = computed(() => {
  const buckets = Array(10).fill(0)
  for (const c of confidences.value) {
    const idx = Math.min(9, Math.floor(c * 10))
    buckets[idx]++
  }
  const max = Math.max(...buckets, 1)
  return buckets.map((count, i) => ({
    count,
    pct:      i * 10,           // bucket start %
    heightPct: (count / max) * 100,
    belowThreshold: (i + 1) * 10 <= pct(props.modelValue),
  }))
})

// ── Live impact ───────────────────────────────────────────────────────────
const kept    = computed(() => props.chords.filter(c => c.confidence >= props.modelValue).length)
const removed = computed(() => props.chords.length - kept.value)

// Hover preview for presets
const hoveredPreset = ref(null)
function previewCount(threshold) {
  return props.chords.filter(c => c.confidence >= threshold / 100).length
}

// ── Helpers ───────────────────────────────────────────────────────────────
const pct = (v) => Math.round(v * 100)

function onInput(e) {
  emit('update:modelValue', Number(e.target.value) / 100)
}

function applyPreset(threshold) {
  emit('update:modelValue', threshold / 100)
}

function applyAuto() {
  emit('update:modelValue', Math.round(stats.value.auto * 20) / 20)  // round to 5%
}

// Zone colour: green when removing little, amber when moderate, red when aggressive
const zoneClass = computed(() => {
  const r = removed.value / Math.max(props.chords.length, 1)
  if (r === 0)    return 'text-chord-muted'
  if (r < 0.2)    return 'text-emerald-400'
  if (r < 0.5)    return 'text-amber-400'
  return 'text-red-400'
})

const PRESETS = [
  { label: 'All',  value: 0  },
  { label: '≥50%', value: 50 },
  { label: '≥65%', value: 65 },
  { label: '≥80%', value: 80 },
]
</script>

<template>
  <div class="card space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <h3 class="label">Confidence Filter</h3>
      <div class="flex items-center gap-3">
        <!-- Auto button -->
        <button
          @click="applyAuto"
          class="text-xs font-mono px-2.5 py-1 rounded-lg border transition-colors
                 border-chord-border text-chord-muted hover:border-chord-accent/50
                 hover:text-chord-accent"
          :title="`Smart threshold based on your track's distribution (≈${pct(stats.auto)}%)`"
        >
          Auto
        </button>
        <!-- Live count -->
        <span class="font-mono text-sm font-semibold" :class="zoneClass">
          {{ kept }} / {{ chords.length }}
        </span>
      </div>
    </div>

    <!-- Histogram -->
    <div v-if="chords.length" class="space-y-1">
      <div class="flex items-end gap-0.5 h-12">
        <div
          v-for="(bucket, i) in histogram" :key="i"
          class="flex-1 rounded-sm transition-all duration-200 min-h-[2px]"
          :class="bucket.pct < pct(modelValue)
            ? 'bg-chord-border opacity-40'
            : 'bg-chord-accent/60'"
          :style="{ height: `${Math.max(4, bucket.heightPct)}%` }"
          :title="`${bucket.pct}–${bucket.pct+10}%: ${bucket.count} chord${bucket.count!==1?'s':''}`"
        />
      </div>
      <!-- X axis labels -->
      <div class="flex justify-between px-0">
        <span class="label" style="font-size:10px">0%</span>
        <span class="label" style="font-size:10px">50%</span>
        <span class="label" style="font-size:10px">100%</span>
      </div>
    </div>

    <!-- Slider -->
    <div class="flex items-center gap-3">
      <div class="relative flex-1">
        <!-- Filled track -->
        <div class="absolute top-1/2 left-0 h-1.5 bg-chord-accent/40 rounded-full
                    pointer-events-none -translate-y-1/2"
             :style="{ width: `${pct(modelValue)}%` }" />
        <input
          type="range" min="0" max="100" step="5"
          :value="pct(modelValue)"
          @input="onInput"
          class="w-full h-1.5 rounded-full appearance-none bg-chord-border
                 cursor-pointer accent-chord-accent relative"
        />
      </div>
      <!-- Threshold badge -->
      <span class="font-mono text-sm font-bold w-12 text-right shrink-0"
            :class="modelValue > 0 ? 'text-chord-accent' : 'text-chord-muted'">
        ≥{{ pct(modelValue) }}%
      </span>
    </div>

    <!-- Impact summary -->
    <div v-if="chords.length && removed > 0"
         class="flex items-center gap-2 text-xs font-mono py-1.5 px-3
                rounded-lg bg-chord-surface border border-chord-border/60">
      <span class="text-emerald-400">{{ kept }} kept</span>
      <span class="text-chord-border">·</span>
      <span :class="zoneClass">{{ removed }} removed</span>
      <span class="text-chord-border ml-auto">·</span>
      <span class="text-chord-muted">
        auto ≈ {{ pct(stats.auto) }}%
      </span>
    </div>

    <!-- Preset buttons with hover preview -->
    <div class="flex gap-2 flex-wrap">
      <button
        v-for="preset in PRESETS" :key="preset.value"
        @click="applyPreset(preset.value)"
        @mouseenter="hoveredPreset = preset.value"
        @mouseleave="hoveredPreset = null"
        class="relative px-3 py-1.5 rounded-lg text-xs font-mono transition-all
               duration-150 border"
        :class="pct(modelValue) === preset.value
          ? 'bg-chord-accent text-white border-chord-accent'
          : 'bg-chord-surface text-chord-muted border-chord-border hover:border-chord-accent/50'"
      >
        {{ preset.label }}
        <!-- Hover preview bubble -->
        <span
          v-if="hoveredPreset === preset.value && chords.length"
          class="absolute -top-7 left-1/2 -translate-x-1/2 whitespace-nowrap
                 bg-chord-border text-chord-text text-xs px-2 py-0.5 rounded-md
                 pointer-events-none z-10"
        >
          {{ previewCount(preset.value) }} chords
        </span>
      </button>
    </div>

  </div>
</template>
