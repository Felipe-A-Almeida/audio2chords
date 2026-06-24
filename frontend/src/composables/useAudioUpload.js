import { ref } from 'vue'
import axios from 'axios'

export function useAudioUpload() {
  const state    = ref('idle')
  const progress = ref(0)
  const error    = ref(null)
  const result   = ref(null)

  async function upload(file, stemMode = 'harmonic') {
    state.value    = 'uploading'
    progress.value = 0
    error.value    = null
    result.value   = null

    const form = new FormData()
    form.append('file', file)
    form.append('stem_mode', stemMode)

    try {
      const response = await axios.post('/api/analysis/upload', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress(evt) {
          if (evt.total) progress.value = Math.round((evt.loaded / evt.total) * 100)
        }
      })
      result.value = response.data
      state.value  = 'done'
    } catch (err) {
      const msg = err.response?.data?.detail?.detail
             || err.response?.data?.detail
             || 'Upload failed. Please try again.'
      error.value = msg
      state.value = 'error'
    }
  }

  function reset() {
    state.value = 'idle'; progress.value = 0
    error.value = null;   result.value   = null
  }

  return { state, progress, error, result, upload, reset }
}
