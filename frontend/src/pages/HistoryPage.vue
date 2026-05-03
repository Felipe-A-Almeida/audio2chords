<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { formatDuration } from '@/utils/formatters'

const router  = useRouter()
const history = ref([])
const loading = ref(true)
const error   = ref(null)

onMounted(async () => {
  try {
    const res = await axios.get('/api/history')
    history.value = res.data
  } catch (e) {
    error.value = 'Could not load history.'
  } finally {
    loading.value = false
  }
})

async function openAnalysis(id) {
  try {
    const res = await axios.get(`/api/analysis/${id}`)
    sessionStorage.setItem('audiochord_result', JSON.stringify(res.data))
    router.push({ name: 'results' })
  } catch {
    error.value = 'Could not load this analysis.'
  }
}

function formatDate(iso) {
  return new Date(iso).toLocaleString()
}
</script>

<template>
  <div class="max-w-3xl mx-auto px-6 py-12 animate-fade-up">
    <div class="flex items-center justify-between mb-8">
      <div>
        <p class="label mb-1">Analysis history</p>
        <h2 class="font-display font-bold text-2xl">Recent tracks</h2>
      </div>
      <RouterLink to="/" class="btn-primary text-sm">
        + New analysis
      </RouterLink>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-6 h-6 border-2 border-chord-accent border-t-transparent
                  rounded-full animate-spin"></div>
    </div>

    <!-- Error -->
    <p v-else-if="error" class="text-red-400 font-mono text-sm text-center py-10">
      {{ error }}
    </p>

    <!-- Empty state -->
    <div v-else-if="!history.length"
         class="card text-center py-16 text-chord-muted">
      <p class="text-4xl mb-4">🎵</p>
      <p class="font-display font-semibold">No analyses yet</p>
      <p class="text-sm mt-1">Upload a track to get started.</p>
    </div>

    <!-- History list -->
    <div v-else class="space-y-3">
      <div
        v-for="item in history" :key="item.id"
        class="card flex items-center gap-4 cursor-pointer
               hover:border-chord-accent/50 transition-colors group"
        @click="openAnalysis(item.id)"
      >
        <!-- Format badge -->
        <div class="w-10 h-10 rounded-xl bg-chord-accent/10 flex items-center
                    justify-center shrink-0 group-hover:bg-chord-accent/20 transition-colors">
          <span class="font-mono text-xs font-bold text-chord-accent uppercase">
            {{ item.format }}
          </span>
        </div>

        <div class="flex-1 min-w-0">
          <p class="font-display font-semibold text-chord-text truncate">
            {{ item.filename }}
          </p>
          <p class="text-chord-muted text-xs font-mono mt-0.5">
            {{ formatDate(item.created_at) }}
          </p>
        </div>

        <svg class="w-5 h-5 text-chord-muted group-hover:text-chord-accent transition-colors shrink-0"
             fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/>
        </svg>
      </div>
    </div>
  </div>
</template>
