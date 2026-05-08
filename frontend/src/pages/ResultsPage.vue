<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysis }      from '@/composables/useAnalysis'
import { usePlayback }      from '@/composables/usePlayback'
import { useChordFilter }   from '@/composables/useChordFilter'
import MetadataCard         from '@/components/ui/MetadataCard.vue'
import AudioPlayer          from '@/components/ui/AudioPlayer.vue'
import ConfidenceFilter     from '@/components/ui/ConfidenceFilter.vue'
import ChordFilterPanel     from '@/components/ui/ChordFilterPanel.vue'
import WaveformChart        from '@/components/charts/WaveformChart.vue'
import SpectrogramChart     from '@/components/charts/SpectrogramChart.vue'
import ChordTimeline        from '@/components/charts/ChordTimeline.vue'
import ChordViewer          from '@/components/charts/ChordViewer.vue'

const router    = useRouter()
const rawResult = ref(null)
const minConfidence = ref(0)

onMounted(() => {
  const stored = sessionStorage.getItem('audiochord_result')
  if (!stored) { router.push({ name: 'upload' }); return }
  rawResult.value = JSON.parse(stored)
  // Set smart default threshold based on track distribution
  const vals = rawResult.value.chords.map(c => c.confidence)
  if (vals.length) {
    const mean = vals.reduce((a,b)=>a+b,0)/vals.length
    const std  = Math.sqrt(vals.reduce((a,b)=>a+(b-mean)**2,0)/vals.length)
    minConfidence.value = Math.round(Math.max(0, mean - 0.5*std) * 20) / 20
  }
})

const {
  bpmLabel, keyLabel, duration, filename,
  chords, waveform, spectrogram, audioUrl, exportJson,
} = useAnalysis(rawResult)

// ── Chord filters ─────────────────────────────────────────────────────────
const {
  hiddenChords,
  hiddenEvents,
  uniqueChords,
  toggleChordName,
  toggleEvent,
  showAllChords,
  hideAllChords,
  globallyVisibleChords,
} = useChordFilter(chords)

// ── Playback ──────────────────────────────────────────────────────────────
const playback = usePlayback()

// Feed globally visible chords (after name filter) into the playback sync
watch(globallyVisibleChords, list => {
  if (list.length) playback.setChords(list)
}, { immediate: true })

// ── Derived counts ────────────────────────────────────────────────────────
const visibleCount = computed(() =>
  chords.value.filter(c =>
    !hiddenChords.value.has(c.chord) && c.confidence >= minConfidence.value
  ).length
)

function fmt(s) {
  return `${String(Math.floor(s/60)).padStart(2,'0')}:${String(Math.floor(s%60)).padStart(2,'0')}`
}

function analyzeAnother() {
  sessionStorage.removeItem('audiochord_result')
  router.push({ name: 'upload' })
}
</script>

<template>
  <div v-if="rawResult" class="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-12
             space-y-4 sm:space-y-6 animate-fade-up">

    <!-- Top bar -->
    <div class="flex items-start justify-between gap-4 flex-wrap">
      <div class="min-w-0">
        <p class="label mb-1">Analysis complete</p>
        <h2 class="font-display font-bold text-xl sm:text-2xl truncate">{{ filename }}</h2>
        <p class="text-chord-muted text-sm mt-1">{{ rawResult.summary }}</p>
      </div>
      <div class="flex gap-2 sm:gap-3 flex-wrap shrink-0">
        <RouterLink to="/history"
          class="btn-primary bg-chord-surface border border-chord-border
                 text-chord-text hover:bg-chord-border text-xs sm:text-sm">
          History
        </RouterLink>
        <button @click="exportJson"
          class="btn-primary bg-chord-surface border border-chord-border
                 text-chord-text hover:bg-chord-border text-xs sm:text-sm">
          Export JSON
        </button>
        <button @click="analyzeAnother" class="btn-primary text-xs sm:text-sm">
          + New
        </button>
      </div>
    </div>

    <!-- ① Player -->
    <AudioPlayer v-if="audioUrl" :playback="playback" :audioUrl="audioUrl" />

    <!-- ② Chord viewer — hero, reacts to globallyVisibleChords -->
    <ChordViewer
      v-if="globallyVisibleChords.length"
      :chords="globallyVisibleChords"
      :currentTime="playback.currentTime.value"
    />

    <!-- ③ Key metrics -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
      <div class="card text-center">
        <p class="label mb-1 sm:mb-2">Tempo</p>
        <p class="value text-xl sm:text-2xl">{{ bpmLabel }}</p>
        <p class="label mt-1">BPM</p>
      </div>
      <div class="card text-center">
        <p class="label mb-1 sm:mb-2">Key</p>
        <p class="value text-xl sm:text-2xl text-chord-accent">{{ keyLabel }}</p>
      </div>
      <div class="card text-center">
        <p class="label mb-1 sm:mb-2">Duration</p>
        <p class="value text-xl sm:text-2xl">{{ fmt(duration) }}</p>
      </div>
      <div class="card text-center">
        <p class="label mb-1 sm:mb-2">Chords</p>
        <p class="value text-xl sm:text-2xl">{{ visibleCount }}</p>
        <p class="label mt-1">
          <span v-if="visibleCount < chords.length" class="text-chord-accent">
            of {{ chords.length }}
          </span>
          <span v-else>detected</span>
        </p>
      </div>
    </div>

    <!-- ④ Filter controls — side by side on desktop, stacked on mobile -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <ConfidenceFilter v-model="minConfidence" :chords="chords" />
      <ChordFilterPanel
        :uniqueChords="uniqueChords"
        :hiddenChords="hiddenChords"
        @toggle="toggleChordName"
        @showAll="showAllChords"
        @hideAll="hideAllChords"
      />
    </div>

    <!-- ⑤ Waveform + Spectrogram -->
    <WaveformChart
      v-if="waveform.length"
      :samples="waveform"
      :duration="duration"
    />
    <SpectrogramChart
      v-if="spectrogram && spectrogram.values?.length > 1"
      :spectrogram="spectrogram"
    />

    <!-- ⑥ Chord Progression + Metadata -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="md:col-span-2">
        <ChordTimeline
          :chords="chords"
          :duration="duration"
          :currentTime="playback.currentTime.value"
          :minConfidence="minConfidence"
          :hiddenChords="hiddenChords"
          :hiddenEvents="hiddenEvents"
          :onSeek="playback.seek"
          @toggleEvent="toggleEvent"
        />
      </div>
      <MetadataCard :metadata="rawResult.metadata" />
    </div>

  </div>

  <div v-else class="flex items-center justify-center min-h-[60vh]">
    <p class="text-chord-muted font-mono text-sm">Loading results…</p>
  </div>
</template>
