import { ref } from 'vue'

export function useLoading(initial = false) {
  const loading = ref(initial)
  const start = () => { loading.value = true }
  const stop = () => { loading.value = false }
  return { loading, start, stop }
}
