<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  spectrogram: { type: Object, required: true },
  // { values: float[][], time_axis: float[], frequency_axis: float[], db_min, db_max }
})

const canvas = ref(null)

function draw() {
  const { values, db_min, db_max } = props.spectrogram
  if (!values?.length || !canvas.value) return

  const rows = values.length       // time frames
  const cols = values[0]?.length   // frequency bins

  const cvs = canvas.value
  cvs.width  = rows
  cvs.height = cols

  const ctx = cvs.getContext('2d')
  const img = ctx.createImageData(rows, cols)

  for (let t = 0; t < rows; t++) {
    for (let f = 0; f < cols; f++) {
      const norm  = (values[t][f] - db_min) / (db_max - db_min)
      const clamped = Math.max(0, Math.min(1, norm))

      // Viridis-inspired: dark-purple → teal → yellow
      const r = Math.round(clamped < 0.5
        ? clamped * 2 * 80
        : 80 + (clamped - 0.5) * 2 * 175)
      const g = Math.round(clamped * 230)
      const b = Math.round(clamped < 0.5
        ? 120 + clamped * 2 * 80
        : 200 - (clamped - 0.5) * 2 * 160)

      // Canvas is flipped vertically so low freq is at bottom
      const idx = ((cols - 1 - f) * rows + t) * 4
      img.data[idx]     = r
      img.data[idx + 1] = g
      img.data[idx + 2] = b
      img.data[idx + 3] = 255
    }
  }
  ctx.putImageData(img, 0, 0)
}

onMounted(draw)
watch(() => props.spectrogram, draw)
</script>

<template>
  <div class="card">
    <h3 class="label mb-4">Spectrogram <span class="text-chord-muted">(mel · dB)</span></h3>
    <div class="w-full overflow-hidden rounded-lg">
      <canvas
        ref="canvas"
        class="w-full h-40 object-fill"
        style="image-rendering: pixelated"
      ></canvas>
    </div>
    <div class="flex justify-between mt-2">
      <span class="label">{{ props.spectrogram.db_min }} dB</span>
      <span class="label">{{ props.spectrogram.db_max }} dB</span>
    </div>
  </div>
</template>
