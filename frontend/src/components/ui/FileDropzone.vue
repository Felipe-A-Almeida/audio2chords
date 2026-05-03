<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  accept: { type: String, default: '.mp3,.wav' },
  maxMb:  { type: Number, default: 50 },
})

const emit = defineEmits(['select'])

const dragging  = ref(false)
const fileError = ref(null)

const allowed = computed(() => props.accept.split(',').map(e => e.trim().replace('.', '')))

function validate(file) {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!allowed.value.includes(ext))
    return `Format .${ext} not supported. Use MP3 or WAV.`
  if (file.size > props.maxMb * 1024 * 1024)
    return `File exceeds ${props.maxMb} MB limit.`
  return null
}

function handleFile(file) {
  if (!file) return
  fileError.value = validate(file)
  if (!fileError.value) emit('select', file)
}

function onDrop(e) {
  dragging.value = false
  const file = e.dataTransfer?.files?.[0]
  handleFile(file)
}

function onInput(e) {
  handleFile(e.target.files?.[0])
}
</script>

<template>
  <div>
    <label
      class="relative flex flex-col items-center justify-center gap-4 min-h-[260px]
             border-2 border-dashed rounded-2xl cursor-pointer select-none
             transition-all duration-300"
      :class="dragging
        ? 'border-chord-accent bg-violet-950/30 scale-[1.01]'
        : 'border-chord-border hover:border-violet-600 hover:bg-chord-surface/60'"
      @dragover.prevent="dragging = true"
      @dragleave.prevent="dragging = false"
      @drop.prevent="onDrop"
    >
      <!-- Icon -->
      <div class="w-16 h-16 rounded-2xl flex items-center justify-center transition-colors"
           :class="dragging ? 'bg-chord-accent' : 'bg-chord-border'">
        <svg class="w-8 h-8" :class="dragging ? 'text-white' : 'text-chord-muted'"
             fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
          <path stroke-linecap="round" stroke-linejoin="round"
                d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803
                   1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9
                   5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803
                   1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z"/>
        </svg>
      </div>

      <div class="text-center">
        <p class="font-display font-semibold text-lg text-chord-text">
          Drop your audio file here
        </p>
        <p class="text-chord-muted text-sm mt-1">
          or <span class="text-chord-accent underline underline-offset-2">browse files</span>
        </p>
        <p class="label mt-3">MP3 · WAV · max {{ maxMb }} MB</p>
      </div>

      <input type="file" :accept="accept" class="sr-only" @change="onInput" />
    </label>

    <p v-if="fileError" class="mt-3 text-red-400 text-sm font-mono text-center">
      {{ fileError }}
    </p>
  </div>
</template>
