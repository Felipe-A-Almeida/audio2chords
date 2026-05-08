<script setup>
/**
 * ConfidenceFilter — slider to set minimum chord confidence threshold.
 * Emits 'update:modelValue' so it works with v-model.
 */
const props = defineProps({
  modelValue: { type: Number, default: 0 },   // 0–1
})
const emit = defineEmits(['update:modelValue'])

function onInput(e) {
  emit('update:modelValue', Number(e.target.value) / 100)
}

const pct = (v) => Math.round(v * 100)
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-3">
      <h3 class="label">Confidence Filter</h3>
      <span class="font-mono text-sm font-semibold"
            :class="modelValue > 0.6 ? 'text-chord-accent' : 'text-chord-muted'">
        ≥ {{ pct(modelValue) }}%
      </span>
    </div>

    <div class="flex items-center gap-3">
      <span class="label text-xs shrink-0">0%</span>

      <div class="relative flex-1">
        <!-- Track fill -->
        <div class="absolute top-1/2 left-0 h-1.5 bg-chord-accent/30 rounded-full
                    pointer-events-none -translate-y-1/2"
             :style="{ width: `${pct(modelValue)}%` }" />
        <input
          type="range"
          min="0" max="100" step="5"
          :value="pct(modelValue)"
          @input="onInput"
          class="w-full h-1.5 rounded-full appearance-none bg-chord-border cursor-pointer
                 relative accent-chord-accent"
        />
      </div>

      <span class="label text-xs shrink-0">100%</span>
    </div>

    <!-- Quick presets -->
    <div class="flex gap-2 mt-3 flex-wrap">
      <button v-for="preset in [0, 50, 70, 85]" :key="preset"
              @click="emit('update:modelValue', preset / 100)"
              class="px-2.5 py-1 rounded-lg text-xs font-mono transition-colors border"
              :class="pct(modelValue) === preset
                ? 'bg-chord-accent text-white border-chord-accent'
                : 'bg-chord-surface text-chord-muted border-chord-border hover:border-chord-accent/50'">
        {{ preset === 0 ? 'All' : `≥${preset}%` }}
      </button>
    </div>
  </div>
</template>
