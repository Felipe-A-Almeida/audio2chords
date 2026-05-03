<script setup>
import { computed } from 'vue'
import { formatDuration, formatFileSize } from '@/utils/formatters'

const props = defineProps({
  metadata: { type: Object, required: true }
})

const rows = computed(() => [
  { label: 'File',       value: props.metadata.filename },
  { label: 'Format',     value: props.metadata.format.toUpperCase() },
  { label: 'Duration',   value: formatDuration(props.metadata.duration_seconds) },
  { label: 'Sample rate',value: `${props.metadata.sample_rate.toLocaleString()} Hz` },
  { label: 'Channels',   value: props.metadata.channels === 1 ? 'Mono' : 'Stereo' },
  { label: 'File size',  value: formatFileSize(props.metadata.file_size_bytes) },
])
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">File Metadata</h3>
    <dl class="space-y-2">
      <div v-for="row in rows" :key="row.label"
           class="flex items-baseline justify-between gap-4 py-1.5
                  border-b border-chord-border/50 last:border-0">
        <dt class="text-chord-muted text-sm shrink-0">{{ row.label }}</dt>
        <dd class="font-mono text-sm text-chord-text truncate text-right">{{ row.value }}</dd>
      </div>
    </dl>
  </div>
</template>
