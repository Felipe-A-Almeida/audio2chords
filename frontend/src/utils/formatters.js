/**
 * Format float seconds to mm:ss string.
 * e.g. 75.3 → "01:15"
 */
export function formatDuration(seconds) {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

/**
 * Format bytes to human-readable string.
 * e.g. 4823142 → "4.6 MB"
 */
export function formatFileSize(bytes) {
  if (bytes < 1024)        return `${bytes} B`
  if (bytes < 1024 ** 2)   return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 ** 2).toFixed(1)} MB`
}

/**
 * Format seconds timestamp to "00:00" for chord timeline labels.
 */
export function formatTimestamp(seconds) {
  return formatDuration(seconds)
}
