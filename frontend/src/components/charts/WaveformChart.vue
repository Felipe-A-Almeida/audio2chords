<script setup>
/**
 * WaveformChart v2 — waveform with beat grid overlay.
 *
 * New props:
 *   beatTimes     : float[] — seconds of each beat (thin markers)
 *   downbeatTimes : float[] — seconds of each bar start (tall markers)
 *   currentTime   : float  — playback position (moving playhead)
 *   showGrid      : bool   — toggle the beat grid on/off
 */
import { ref, onMounted, watch, computed } from 'vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

const props = defineProps({
  samples:       { type: Array,   required: true },
  duration:      { type: Number,  required: true },
  beatTimes:     { type: Array,   default: () => [] },
  downbeatTimes: { type: Array,   default: () => [] },
  currentTime:   { type: Number,  default: 0 },
  showGrid:      { type: Boolean, default: true },
})

const canvas      = ref(null)
const overlayCanvas = ref(null)   // separate canvas for beat lines + playhead
let chart = null

// ── Waveform chart ────────────────────────────────────────────────────────
function buildChart() {
  if (chart) chart.destroy()

  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels: props.samples.map((_, i) =>
        ((i / props.samples.length) * props.duration).toFixed(1)
      ),
      datasets: [{
        data: props.samples,
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
      animation: { duration: 500, easing: 'easeOutCubic' },
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

// ── Beat grid + playhead overlay ──────────────────────────────────────────
// Drawn on a transparent canvas stacked on top of the Chart.js canvas.
// This avoids rebuilding the entire chart on every animation frame.
function drawOverlay() {
  const cvs = overlayCanvas.value
  if (!cvs) return
  const ctx = cvs.getContext('2d')
  ctx.clearRect(0, 0, cvs.width, cvs.height)

  if (!props.duration) return

  // Chart.js internal plot area (accounts for axis padding)
  // We derive it from the chart instance if available
  const plotLeft   = chart?.chartArea?.left   ?? 40
  const plotRight  = chart?.chartArea?.right  ?? cvs.width - 8
  const plotTop    = chart?.chartArea?.top    ?? 4
  const plotBottom = chart?.chartArea?.bottom ?? cvs.height - 24
  const plotW = plotRight - plotLeft
  const plotH = plotBottom - plotTop

  function timeToX(t) {
    return plotLeft + (t / props.duration) * plotW
  }

  // ── Beat lines (thin, subtle) ─────────────────────────────────────────
  if (props.showGrid && props.beatTimes.length) {
    ctx.strokeStyle = 'rgba(124, 58, 237, 0.18)'
    ctx.lineWidth   = 1
    for (const t of props.beatTimes) {
      const x = timeToX(t)
      if (x < plotLeft || x > plotRight) continue
      ctx.beginPath()
      ctx.moveTo(x, plotTop)
      ctx.lineTo(x, plotBottom)
      ctx.stroke()
    }
  }

  // ── Downbeat lines (taller, more opaque + label) ─────────────────────
  if (props.showGrid && props.downbeatTimes.length) {
    ctx.strokeStyle = 'rgba(124, 58, 237, 0.50)'
    ctx.lineWidth   = 1.5
    ctx.fillStyle   = 'rgba(124, 58, 237, 0.70)'
    ctx.font        = '9px JetBrains Mono, monospace'
    ctx.textAlign   = 'center'

    props.downbeatTimes.forEach((t, barIdx) => {
      const x = timeToX(t)
      if (x < plotLeft || x > plotRight) return
      ctx.beginPath()
      ctx.moveTo(x, plotTop - 4)
      ctx.lineTo(x, plotBottom)
      ctx.stroke()

      // Bar number label above the line
      ctx.fillText(`${barIdx + 1}`, x, plotTop - 6)
    })
  }

  // ── Playhead ──────────────────────────────────────────────────────────
  if (props.currentTime > 0) {
    const x = timeToX(props.currentTime)
    if (x >= plotLeft && x <= plotRight) {
      // Glow effect — draw twice, blurred then sharp
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)'
      ctx.lineWidth   = 5
      ctx.beginPath()
      ctx.moveTo(x, plotTop)
      ctx.lineTo(x, plotBottom)
      ctx.stroke()

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.90)'
      ctx.lineWidth   = 1.5
      ctx.beginPath()
      ctx.moveTo(x, plotTop)
      ctx.lineTo(x, plotBottom)
      ctx.stroke()

      // Playhead triangle at top
      ctx.fillStyle = 'rgba(255, 255, 255, 0.90)'
      ctx.beginPath()
      ctx.moveTo(x - 4, plotTop)
      ctx.lineTo(x + 4, plotTop)
      ctx.lineTo(x,     plotTop + 7)
      ctx.closePath()
      ctx.fill()
    }
  }
}

// Keep overlay canvas in sync with container size
function syncSize() {
  const cvs = overlayCanvas.value
  const ref = canvas.value
  if (!cvs || !ref) return
  cvs.width  = ref.offsetWidth  || ref.width
  cvs.height = ref.offsetHeight || ref.height
}

onMounted(() => {
  buildChart()
  syncSize()
  drawOverlay()
})

// Rebuild chart when samples change
watch(() => props.samples, () => { buildChart(); drawOverlay() })

// Redraw overlay only when beat/playhead data changes (cheap)
watch(
  [() => props.currentTime, () => props.showGrid, () => props.beatTimes],
  () => { syncSize(); drawOverlay() }
)
</script>

<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
      <h3 class="label">Waveform</h3>
      <div class="flex items-center gap-3">
        <!-- Beat grid toggle -->
        <label v-if="beatTimes.length"
               class="flex items-center gap-2 cursor-pointer select-none">
          <div class="relative">
            <input type="checkbox" :checked="showGrid"
                   class="sr-only peer"
                   @change="$emit('update:showGrid', $event.target.checked)" />
            <div class="w-8 h-4 bg-chord-border rounded-full peer
                        peer-checked:bg-chord-accent transition-colors"></div>
            <div class="absolute top-0.5 left-0.5 w-3 h-3 bg-white rounded-full
                        shadow transition-all peer-checked:translate-x-4"></div>
          </div>
          <span class="label text-xs">Beat grid</span>
        </label>

        <!-- Beat count badge -->
        <span v-if="beatTimes.length && showGrid"
              class="font-mono text-xs text-chord-muted">
          {{ beatTimes.length }} beats · {{ downbeatTimes.length }} bars
        </span>
      </div>
    </div>

    <!-- Stacked canvas container -->
    <div class="relative h-36">
      <!-- Chart.js waveform -->
      <canvas ref="canvas" class="absolute inset-0 w-full h-full"></canvas>
      <!-- Beat grid + playhead overlay -->
      <canvas ref="overlayCanvas"
              class="absolute inset-0 w-full h-full pointer-events-none"></canvas>
    </div>
  </div>
</template>
