<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysis } from '@/composables/useAnalysis'
import MetadataCard    from '@/components/ui/MetadataCard.vue'
import WaveformChart   from '@/components/charts/WaveformChart.vue'
import SpectrogramChart from '@/components/charts/SpectrogramChart.vue'
import ChordTimeline   from '@/components/charts/ChordTimeline.vue'

const router = useRouter()
const rawResult = ref(null)

onMounted(() => {
  const stored = sessionStorage.getItem('audiochord_result')
  if (!stored) { router.push({ name: 'upload' }); return }
  rawResult.value = JSON.parse(stored)
})

const { bpmLabel, keyLabel, duration, filename, chords, waveform, spectrogram, exportJson } =
  useAnalysis(rawResult)

function analyzeAnother() {
  sessionStorage.removeItem('audiochord_result')
  router.push({ name: 'upload' })
}
</script>

<template>
  <div v-if="rawResult" class="max-w-6xl mx-auto px-6 py-12 space-y-8 animate-fade-up">

    <!-- Top bar -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <p class="label mb-1">Analysis complete</p>
        <h2 class="font-display font-bold text-2xl truncate max-w-lg">{{ filename }}</h2>
        <p class="text-chord-muted text-sm mt-1">{{ rawResult.summary }}</p>
      </div>
      <div class="flex gap-3">
        <button @click="exportJson" class="btn-primary bg-chord-surface border border-chord-border
               text-chord-text hover:bg-chord-border">
          Export JSON
        </button>
        <button @click="analyzeAnother" class="btn-primary">
          Analyze Another
        </button>
      </div>
    </div>

    <!-- Key metrics -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="card text-center">
        <p class="label mb-2">Tempo</p>
        <p class="value">{{ bpmLabel }}</p>
        <p class="label mt-1">BPM</p>
      </div>
      <div class="card text-center">
        <p class="label mb-2">Key</p>
        <p class="value text-chord-accent">{{ keyLabel }}</p>
      </div>
      <div class="card text-center">
        <p class="label mb-2">Duration</p>
        <p class="value">{{ rawResult.metadata ? Math.floor(duration / 60) + ':' + String(Math.floor(duration % 60)).padStart(2,'0') : '—' }}</p>
      </div>
      <div class="card text-center">
        <p class="label mb-2">Chords</p>
        <p class="value">{{ chords.length }}</p>
        <p class="label mt-1">detected</p>
      </div>
    </div>

    <!-- Charts row -->
    <div class="space-y-4">
      <WaveformChart
        v-if="waveform.length"
        :samples="waveform"
        :duration="duration"
      />
      <SpectrogramChart
        v-if="spectrogram && spectrogram.values?.length > 1"
        :spectrogram="spectrogram"
      />
    </div>

    <!-- Bottom row -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="md:col-span-2">
        <ChordTimeline :chords="chords" :duration="duration" />
      </div>
      <MetadataCard :metadata="rawResult.metadata" />
    </div>

  </div>

  <!-- Loading / redirect state -->
  <div v-else class="flex items-center justify-center min-h-[60vh]">
    <p class="text-chord-muted font-mono text-sm">Loading results…</p>
  </div>
</template>
