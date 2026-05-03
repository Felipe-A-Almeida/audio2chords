<script setup>
import { ref, onMounted, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const props = defineProps({
  samples:  { type: Array, required: true },  // float[] normalised -1..1
  duration: { type: Number, required: true },  // seconds
})

const canvas = ref(null)
let chart    = null

function buildChart() {
  if (chart) chart.destroy()

  // Downsample further for performance if needed
  const data = props.samples

  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: data.map((_, i) => {
        const t = (i / data.length) * props.duration
        return t.toFixed(1)
      }),
      datasets: [{
        data,
        borderColor: '#7C3AED',
        borderWidth: 1,
        backgroundColor: 'rgba(124,58,237,0.08)',
        fill: true,
        pointRadius: 0,
        tension: 0.2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600, easing: 'easeOutCubic' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: {
          ticks: {
            color: '#6B7280',
            font: { family: 'JetBrains Mono', size: 10 },
            maxTicksLimit: 10,
          },
          grid:  { color: '#1E1E2E' },
          border: { color: '#1E1E2E' },
        },
        y: {
          min: -1, max: 1,
          ticks: { color: '#6B7280', font: { family: 'JetBrains Mono', size: 10 } },
          grid:  { color: '#1E1E2E' },
          border: { color: '#1E1E2E' },
        }
      }
    }
  })
}

onMounted(buildChart)
watch(() => props.samples, buildChart)
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">Waveform</h3>
    <div class="h-36">
      <canvas ref="canvas"></canvas>
    </div>
  </div>
</template>
