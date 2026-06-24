<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { formatDuration } from '@/utils/formatters'

const props = defineProps({
  playback: { type: Object, required: true },
  audioUrl: { type: String, required: true },
})

const audioRef    = ref(null)
const volume      = ref(1)       // 0–1
const isMuted     = ref(false)
const showSlider  = ref(false)

onMounted(() => { if (audioRef.value) props.playback.attachElement(audioRef.value) })
onUnmounted(() => { props.playback.detachElement() })

// The actual volume applied to the element (0 when muted)
const effectiveVolume = computed(() => isMuted.value ? 0 : volume.value)

function setVolume(val) {
  volume.value = val
  isMuted.value = val === 0
  if (audioRef.value) audioRef.value.volume = effectiveVolume.value
}

function toggleMute() {
  isMuted.value = !isMuted.value
  if (audioRef.value) audioRef.value.volume = effectiveVolume.value
}

function onVolumeInput(e) {
  setVolume(Number(e.target.value))
}

function onProgressClick(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  props.playback.seek(ratio * props.playback.duration.value)
}

// Icon helpers
const volumeIcon = computed(() => {
  if (isMuted.value || volume.value === 0) return 'mute'
  if (volume.value < 0.4) return 'low'
  if (volume.value < 0.7) return 'mid'
  return 'high'
})
</script>

<template>
  <div class="card">
    <audio ref="audioRef" :src="audioUrl" preload="metadata" class="hidden" />

    <div class="flex items-center gap-3 sm:gap-4">

      <!-- Play / Pause -->
      <button
        @click="playback.toggle()"
        class="w-11 h-11 sm:w-12 sm:h-12 rounded-full bg-chord-accent hover:bg-violet-500
               flex items-center justify-center shrink-0 transition-colors"
      >
        <svg v-if="!playback.isPlaying.value" class="w-5 h-5 text-white ml-0.5"
             fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z"/>
        </svg>
        <svg v-else class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
        </svg>
      </button>

      <!-- Progress bar + timestamps -->
      <div class="flex-1 space-y-1.5 min-w-0">
        <div class="h-2 bg-chord-border rounded-full cursor-pointer relative overflow-hidden"
             @click="onProgressClick">
          <div class="h-full bg-chord-accent rounded-full transition-all duration-100"
               :style="{ width: `${playback.progress.value * 100}%` }" />
        </div>
        <div class="flex justify-between">
          <span class="font-mono text-xs text-chord-muted">
            {{ formatDuration(playback.currentTime.value) }}
          </span>
          <span class="font-mono text-xs text-chord-muted">
            {{ formatDuration(playback.duration.value) }}
          </span>
        </div>
      </div>

      <!-- Volume control -->
      <div class="relative flex items-center shrink-0">

        <!-- Mute / volume icon button -->
        <button
          @click="toggleMute"
          @mouseenter="showSlider = true"
          class="w-8 h-8 flex items-center justify-center rounded-lg
                 text-chord-muted hover:text-chord-text transition-colors"
          :title="isMuted ? 'Unmute' : 'Mute'"
        >
          <!-- Mute -->
          <svg v-if="volumeIcon === 'mute'" class="w-5 h-5"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M17.25 9.75L19.5 12m0 0l2.25 2.25M19.5 12l2.25-2.25M19.5
                     12l-2.25 2.25m-10.5-6l4.72-4.72a.75.75 0 011.28.531V19.94a.75.75
                     0 01-1.28.53l-4.72-4.72H4.51c-.88 0-1.704-.506-1.938-1.354A9.01
                     9.01 0 012.25 12c0-.83.112-1.633.322-2.395C2.806 8.757 3.63 8.25
                     4.51 8.25H6.75z"/>
          </svg>
          <!-- Low -->
          <svg v-else-if="volumeIcon === 'low'" class="w-5 h-5"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010
                     7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0
                     01-1.28.53L6.75 15.75H4.5a.75.75 0 01-.75-.75v-6a.75.75 0
                     01.75-.75h2.25z" />
          </svg>
          <!-- Mid -->
          <svg v-else-if="volumeIcon === 'mid'" class="w-5 h-5"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19.114 5.636a9 9 0 010 12.728M6.75 8.25l4.72-4.72a.75.75 0
                     011.28.53v15.88a.75.75 0 01-1.28.53L6.75 15.75H4.5a.75.75 0
                     01-.75-.75v-6a.75.75 0 01.75-.75h2.25z" />
          </svg>
          <!-- High -->
          <svg v-else class="w-5 h-5"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M19.114 5.636a9 9 0 010 12.728M16.463 8.288a5.25 5.25 0 010
                     7.424M6.75 8.25l4.72-4.72a.75.75 0 011.28.53v15.88a.75.75 0
                     01-1.28.53L6.75 15.75H4.5a.75.75 0 01-.75-.75v-6a.75.75 0
                     01.75-.75h2.25z"/>
          </svg>
        </button>

        <!-- Slider — appears on hover -->
        <div
          class="absolute right-9 bottom-0 flex items-center gap-2 px-3 py-2
                 bg-chord-surface border border-chord-border rounded-xl shadow-lg
                 transition-all duration-200 origin-right"
          :class="showSlider ? 'opacity-100 scale-x-100' : 'opacity-0 scale-x-0 pointer-events-none'"
          @mouseenter="showSlider = true"
          @mouseleave="showSlider = false"
        >
          <!-- Min icon -->
          <svg class="w-3 h-3 text-chord-muted shrink-0"
               fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 7.97v8.05c1.48-.73
                     2.5-2.25 2.5-4.02z"/>
          </svg>

          <!-- Volume slider -->
          <div class="relative w-24 h-4 flex items-center">
            <!-- Filled track -->
            <div class="absolute left-0 h-1.5 bg-chord-accent rounded-full pointer-events-none"
                 :style="{ width: `${(isMuted ? 0 : volume) * 100}%` }" />
            <input
              type="range"
              min="0" max="1" step="0.02"
              :value="isMuted ? 0 : volume"
              @input="onVolumeInput"
              class="w-full h-1.5 rounded-full appearance-none bg-chord-border
                     cursor-pointer accent-chord-accent relative"
            />
          </div>

          <!-- Max icon -->
          <svg class="w-3.5 h-3.5 text-chord-muted shrink-0"
               fill="currentColor" viewBox="0 0 24 24">
            <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3A4.5 4.5 0 0014 7.97v8.05c1.48-.73
                     2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11
                     5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77 0-4.28-2.99-7.86-7-8.77z"/>
          </svg>

          <!-- Percentage label -->
          <span class="font-mono text-xs text-chord-muted w-7 text-right shrink-0">
            {{ Math.round((isMuted ? 0 : volume) * 100) }}%
          </span>
        </div>
      </div>

    </div>
  </div>
</template>