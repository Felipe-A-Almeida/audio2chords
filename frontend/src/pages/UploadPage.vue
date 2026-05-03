<script setup>
import { watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAudioUpload } from '@/composables/useAudioUpload'
import FileDropzone from '@/components/ui/FileDropzone.vue'
import ProgressBar  from '@/components/ui/ProgressBar.vue'

const router = useRouter()
const { state, progress, error, result, upload } = useAudioUpload()

// Navigate to results once analysis is done
watch(result, (val) => {
  if (val) {
    // Store in sessionStorage so ResultsPage can read it on refresh
    sessionStorage.setItem('audiochord_result', JSON.stringify(val))
    router.push({ name: 'results' })
  }
})

function onFileSelected(file) {
  upload(file)
}

const progressLabel = {
  uploading: 'Uploading…',
  analyzing: 'Analyzing audio…',
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-6 py-20 flex flex-col items-center gap-12 animate-fade-up">

    <!-- Hero -->
    <div class="text-center space-y-3">
      <h1 class="font-display font-extrabold text-5xl tracking-tight leading-none">
        Drop a track.<br/>
        <span class="text-chord-accent">Hear the theory.</span>
      </h1>
      <p class="text-chord-muted text-lg max-w-md mx-auto">
        Upload an MP3 or WAV file and get instant BPM, key, waveform, spectrogram and chord analysis.
      </p>
    </div>

    <!-- Upload area -->
    <div class="w-full">
      <FileDropzone
        v-if="state === 'idle' || state === 'error'"
        @select="onFileSelected"
      />

      <!-- Progress -->
      <div v-if="state === 'uploading'"
           class="card flex flex-col gap-6 items-center py-12">
        <div class="w-16 h-16 rounded-2xl bg-chord-accent/10 flex items-center justify-center">
          <svg class="w-8 h-8 text-chord-accent animate-pulse-slow"
               fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round"
                  d="M9 9l10.5-3m0 6.553v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803
                     1.803 0 11-.99-3.467l2.31-.66a2.25 2.25 0 001.632-2.163zm0 0V2.25L9
                     5.25v10.303m0 0v3.75a2.25 2.25 0 01-1.632 2.163l-1.32.377a1.803
                     1.803 0 01-.99-3.467l2.31-.66A2.25 2.25 0 009 15.553z"/>
          </svg>
        </div>
        <ProgressBar :progress="progress" label="Uploading & analyzing…" />
        <p class="text-chord-muted text-sm">This may take a few seconds for longer files.</p>
      </div>

      <!-- Error state -->
      <div v-if="state === 'error'" class="mt-4 p-4 rounded-xl bg-red-950/40 border border-red-800/50">
        <p class="text-red-400 font-mono text-sm text-center">{{ error }}</p>
      </div>
    </div>

    <!-- Feature chips -->
    <div v-if="state === 'idle'" class="flex flex-wrap gap-2 justify-center">
      <span v-for="f in ['BPM Detection', 'Key Analysis', 'Waveform', 'Spectrogram', 'Chord Timeline', 'JSON Export']"
            :key="f"
            class="px-3 py-1 rounded-full bg-chord-surface border border-chord-border
                   text-xs font-mono text-chord-muted">
        {{ f }}
      </span>
    </div>

  </div>
</template>
