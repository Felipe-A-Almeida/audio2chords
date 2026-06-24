<script setup>
import { computed } from 'vue'
import { formatDuration, formatFileSize } from '@/utils/formatters'

const props = defineProps({
  metadata: { type: Object, required: true },
  stemInfo: { type: Object, default: null },
})

const rows = computed(() => [
  { label: 'File',        value: props.metadata.filename },
  { label: 'Format',      value: props.metadata.format.toUpperCase() },
  { label: 'Duration',    value: formatDuration(props.metadata.duration_seconds) },
  { label: 'Sample rate', value: `${props.metadata.sample_rate.toLocaleString()} Hz` },
  { label: 'Channels',    value: props.metadata.channels === 1 ? 'Mono' : 'Stereo' },
  { label: 'File size',   value: formatFileSize(props.metadata.file_size_bytes) },
])

// Badge config per combination of method + mode
const stemBadge = computed(() => {
  if (!props.stemInfo) return null
  const { method, mode, vocal_removal, demucs_available } = props.stemInfo

  if (vocal_removal) {
    return {
      label: '🎸 Instrumental',
      color: 'bg-emerald-900/40 text-emerald-400 border-emerald-800/50',
      tip:   'Demucs htdemucs — vocals removed, instruments only',
    }
  }
  if (method === 'demucs') {
    return {
      label: '🎵 Demucs',
      color: 'bg-emerald-900/40 text-emerald-400 border-emerald-800/50',
      tip:   'Neural stem separation — vocals + instruments',
    }
  }
  if (mode === 'full') {
    return {
      label: '⚡ Full mix',
      color: 'bg-chord-surface text-chord-muted border-chord-border',
      tip:   'No stem separation — raw audio used for analysis',
    }
  }
  return {
    label: 'HPSS',
    color: 'bg-chord-surface text-chord-muted border-chord-border',
    tip:   'Librosa harmonic-percussive separation',
  }
})

const stemNote = computed(() => {
  if (!props.stemInfo) return null
  const { method, mode, vocal_removal, demucs_available } = props.stemInfo

  if (vocal_removal) return null  // working perfectly, no note needed

  if (mode === 'instrumental' && !demucs_available) {
    return {
      type: 'warning',
      text: 'Vocal removal requested but Demucs is not installed. Used HPSS instead.',
      action: 'pip install demucs',
    }
  }
  if (method === 'hpss' && mode !== 'full') {
    return {
      type: 'info',
      text: 'Install Demucs for higher accuracy on vocal-heavy recordings.',
      action: 'pip install demucs',
    }
  }
  return null
})
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4 gap-2 flex-wrap">
      <h3 class="label">File Metadata</h3>
      <span v-if="stemBadge"
            class="text-xs font-mono px-2 py-0.5 rounded-lg border shrink-0"
            :class="stemBadge.color"
            :title="stemBadge.tip">
        {{ stemBadge.label }}
      </span>
    </div>

    <dl class="space-y-2">
      <div v-for="row in rows" :key="row.label"
           class="flex items-baseline justify-between gap-4 py-1.5
                  border-b border-chord-border/50 last:border-0">
        <dt class="text-chord-muted text-sm shrink-0">{{ row.label }}</dt>
        <dd class="font-mono text-sm text-chord-text truncate text-right">{{ row.value }}</dd>
      </div>
    </dl>

    <!-- Stem note -->
    <div v-if="stemNote" class="mt-3 p-2.5 rounded-lg text-xs font-mono leading-relaxed"
         :class="stemNote.type === 'warning'
           ? 'bg-amber-900/20 border border-amber-800/40 text-amber-400'
           : 'bg-chord-surface border border-chord-border text-chord-muted'">
      <p>{{ stemNote.text }}</p>
      <p class="mt-1">
        <span class="text-chord-accent">{{ stemNote.action }}</span>
      </p>
    </div>
  </div>
</template>
