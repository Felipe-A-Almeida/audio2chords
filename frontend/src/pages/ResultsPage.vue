<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysis }   from '@/composables/useAnalysis'
import { usePlayback }   from '@/composables/usePlayback'
import MetadataCard      from '@/components/ui/MetadataCard.vue'
import AudioPlayer       from '@/components/ui/AudioPlayer.vue'
import WaveformChart     from '@/components/charts/WaveformChart.vue'
import SpectrogramChart  from '@/components/charts/SpectrogramChart.vue'
import ChordTimeline     from '@/components/charts/ChordTimeline.vue'
import ChordViewer       from '@/components/charts/ChordViewer.vue'

const router    = useRouter()
const rawResult = ref(null)

onMounted(() => {
  const stored = sessionStorage.getItem('audiochord_result')
  if (!stored) { router.push({ name: 'upload' }); return }
  rawResult.value = JSON.parse(stored)
})

const {
  bpmLabel, keyLabel, duration, filename,
  chords, waveform, spectrogram, audioUrl, exportJson,
} = useAnalysis(rawResult)

const playback = usePlayback()
watch(chords, (list) => { if (list.length) playback.setChords(list) }, { immediate: true })

function analyzeAnother() {
  sessionStorage.removeItem('audiochord_result')
  router.push({ name: 'upload' })
}

function formatMmSs(s) {
  const m = Math.floor(s / 60)
  return `${String(m).padStart(2,'0')}:${String(Math.floor(s%60)).padStart(2,'0')}`
}
</script>

<template>
  <div v-if="rawResult" class="max-w-6xl mx-auto px-6 py-12 space-y-6 animate-fade-up">

    <!-- Top bar -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div>
        <p class="label mb-1">Analysis complete</p>
        <h2 class="font-display font-bold text-2xl truncate max-w-lg">{{ filename }}</h2>
        <p class="text-chord-muted text-sm mt-1">{{ rawResult.summary }}</p>
      </div>
      <div class="flex gap-3 flex-wrap">
        <RouterLink to="/history"
          class="btn-primary bg-chord-surface border border-chord-border
                 text-chord-text hover:bg-chord-border text-sm">
          History
        </RouterLink>
        <button @click="exportJson"
          class="btn-primary bg-chord-surface border border-chord-border
                 text-chord-text hover:bg-chord-border text-sm">
          Export JSON
        </button>
        <button @click="analyzeAnother" class="btn-primary text-sm">
          + New analysis
        </button>
      </div>
    </div>

    <!-- ① Player -->
    <AudioPlayer v-if="audioUrl" :playback="playback" :audioUrl="audioUrl" />

    <!-- ② Chord diagrams — full width, hero section right below player -->
    <ChordViewer
      v-if="chords.length"
      :chords="chords"
      :currentTime="playback.currentTime.value"
    />

    <!-- ③ Key metrics -->
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
        <p class="value">{{ formatMmSs(duration) }}</p>
      </div>
      <div class="card text-center">
        <p class="label mb-2">Chords</p>
        <p class="value">{{ chords.length }}</p>
        <p class="label mt-1">detected</p>
      </div>
    </div>

    <!-- ④ Waveform + Spectrogram -->
    <WaveformChart
      v-if="waveform.length"
      :samples="waveform"
      :duration="duration"
    />
    <SpectrogramChart
      v-if="spectrogram && spectrogram.values?.length > 1"
      :spectrogram="spectrogram"
    />

    <!-- ⑤ Chord timeline + metadata -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="md:col-span-2">
        <ChordTimeline
          :chords="chords"
          :duration="duration"
          :currentTime="playback.currentTime.value"
          :onSeek="playback.seek"
        />
      </div>
      <MetadataCard :metadata="rawResult.metadata" />
    </div>

  </div>

  <div v-else class="flex items-center justify-center min-h-[60vh]">
    <p class="text-chord-muted font-mono text-sm">Loading results…</p>
  </div>
</template>
