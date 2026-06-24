<script setup>
defineProps({
  progress: { type: Number, default: 0 },   // 0–100
  label:    { type: String, default: 'Analyzing…' },
})
</script>

<template>
  <div class="w-full space-y-3">
    <div class="flex items-center justify-between">
      <span class="label">{{ label }}</span>
      <span class="font-mono text-xs text-chord-accent">{{ progress }}%</span>
    </div>
    <div class="h-1.5 bg-chord-border rounded-full overflow-hidden">
      <div
        class="h-full bg-chord-accent rounded-full transition-all duration-300 ease-out
               relative overflow-hidden"
        :style="{ width: `${progress}%` }"
      >
        <!-- Shimmer sweep -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent
                    animate-[shimmer_1.5s_infinite]" style="background-size:200% 100%"></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes shimmer {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
</style>
