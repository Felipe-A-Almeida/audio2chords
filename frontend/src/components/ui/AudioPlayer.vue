<script setup>
/**
 * AudioPlayer — controls for the hidden <audio> element.
 *
 * Props:
 *   playback   : the object returned by usePlayback()
 *   audioUrl   : string URL for the src attribute
 *
 * This component owns the <audio> element and wires it to the
 * playback composable via attachElement() on mount.
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { formatDuration } from '@/utils/formatters'

const props = defineProps({
  playback: { type: Object, required: true },
  audioUrl: { type: String, required: true },
})

const audioRef = ref(null)

onMounted(() => {
  if (audioRef.value) props.playback.attachElement(audioRef.value)
})

onUnmounted(() => {
  props.playback.detachElement()
})

function onProgressClick(e) {
  const rect = e.currentTarget.getBoundingClientRect()
  const ratio = (e.clientX - rect.left) / rect.width
  props.playback.seek(ratio * props.playback.duration.value)
}
</script>

<template>
  <div class="card">
    <!-- Hidden native audio element — source of truth for currentTime -->
    <audio ref="audioRef" :src="audioUrl" preload="metadata" class="hidden" />

    <div class="flex items-center gap-4">
      <!-- Play / Pause button -->
      <button
        @click="playback.toggle()"
        class="w-12 h-12 rounded-full bg-chord-accent hover:bg-violet-500
               flex items-center justify-center shrink-0 transition-colors"
      >
        <!-- Play icon -->
        <svg v-if="!playback.isPlaying.value" class="w-5 h-5 text-white ml-0.5"
             fill="currentColor" viewBox="0 0 24 24">
          <path d="M8 5v14l11-7z"/>
        </svg>
        <!-- Pause icon -->
        <svg v-else class="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
        </svg>
      </button>

      <!-- Progress bar + timestamps -->
      <div class="flex-1 space-y-1.5">
        <div
          class="h-2 bg-chord-border rounded-full cursor-pointer relative overflow-hidden"
          @click="onProgressClick"
        >
          <div
            class="h-full bg-chord-accent rounded-full transition-all duration-100"
            :style="{ width: `${playback.progress.value * 100}%` }"
          />
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
    </div>
  </div>
</template>
