<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAudioUpload } from '@/composables/useAudioUpload'
import FileDropzone from '@/components/ui/FileDropzone.vue'
import ProgressBar  from '@/components/ui/ProgressBar.vue'

const router   = useRouter()
const stemMode = ref('harmonic')

const { state, progress, error, result, upload } = useAudioUpload()

watch(result, (val) => {
  if (val) {
    sessionStorage.setItem('audiochord_result', JSON.stringify(val))
    router.push({ name: 'results' })
  }
})

function onFileSelected(file) {
  upload(file, stemMode.value)
}

const MODES = [
  {
    value: 'harmonic',
    icon:  '🎵',
    label: 'Harmonic',
    desc:  'Vocals + instruments. Works on all files. Best default.',
  },
  {
    value: 'instrumental',
    icon:  '🎸',
    label: 'Instrumental',
    desc:  'Instruments only — vocals removed. Requires Demucs.',
  },
  {
    value: 'full',
    icon:  '⚡',
    label: 'Full mix',
    desc:  'No separation. Fastest. Less accurate on complex recordings.',
  },
]
</script>

<template>
  <div class="max-w-2xl mx-auto px-6 py-16 flex flex-col items-center gap-10 animate-fade-up">

    <!-- Hero -->
    <div class="text-center space-y-3">
      <h1 class="font-display font-extrabold text-4xl sm:text-5xl tracking-tight leading-none">
        Drop a track.<br/>
        <span class="text-chord-accent">Hear the theory.</span>
      </h1>
      <p class="text-chord-muted text-base sm:text-lg max-w-md mx-auto">
        Upload an MP3 or WAV and get BPM, key, waveform, spectrogram and chord analysis.
      </p>
    </div>

    <!-- Stem mode selector -->
    <div v-if="state === 'idle' || state === 'error'" class="w-full space-y-2">
      <p class="label text-center mb-3">Stem separation mode</p>
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
        <button
          v-for="mode in MODES" :key="mode.value"
          @click="stemMode = mode.value"
          class="flex flex-col items-start gap-1.5 p-4 rounded-xl border
                 text-left transition-all duration-200"
          :class="stemMode === mode.value
            ? 'border-chord-accent bg-chord-accent/10'
            : 'border-chord-border bg-chord-surface hover:border-chord-accent/40'"
        >
          <div class="flex items-center gap-2 w-full">
            <span class="text-lg">{{ mode.icon }}</span>
            <span class="font-display font-semibold text-sm"
                  :class="stemMode === mode.value ? 'text-chord-accent' : 'text-chord-text'">
              {{ mode.label }}
            </span>
            <div v-if="stemMode === mode.value"
                 class="ml-auto w-2 h-2 rounded-full bg-chord-accent shrink-0"></div>
          </div>
          <p class="text-xs text-chord-muted leading-relaxed">{{ mode.desc }}</p>
        </button>
      </div>
    </div>

    <!-- Drop zone -->
    <div class="w-full">
      <FileDropzone
        v-if="state === 'idle' || state === 'error'"
        @select="onFileSelected"
      />

      <div v-if="state === 'uploading'"
           class="card flex flex-col gap-6 items-center py-12">
        <div class="w-14 h-14 rounded-2xl bg-chord-accent/10 flex items-center justify-center">
          <svg class="w-7 h-7 text-chord-accent animate-pulse-slow"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377
                     a1.803 1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0
                     001.632-2.163zm0 0V2.25L9 5.25v10.303m0 0v3.75a2.25 2.25 0
                     01-1.632 2.163l-1.32.377a1.803 1.803 0 01-.99-3.467l2.31-.66
                     A2.25 2.25 0 009 15.553z"/>
          </svg>
        </div>
        <ProgressBar :progress="progress" label="Uploading & analyzing…" />
        <p class="text-chord-muted text-sm font-mono">
          Mode: <span class="text-chord-accent">{{ stemMode }}</span>
        </p>
      </div>

      <div v-if="state === 'error'"
           class="mt-4 p-4 rounded-xl bg-red-950/40 border border-red-800/50">
        <p class="text-red-400 font-mono text-sm text-center">{{ error }}</p>
      </div>
    </div>

    <!-- Feature chips -->
    <div v-if="state === 'idle'" class="flex flex-wrap gap-2 justify-center">
      <span v-for="f in ['BPM Detection','Key Analysis','Waveform',
                         'Spectrogram','Chord Timeline','Stem Separation','JSON Export']"
            :key="f"
            class="px-3 py-1 rounded-full bg-chord-surface border border-chord-border
                   text-xs font-mono text-chord-muted">
        {{ f }}
      </span>
    </div>

  </div>
</template>
