import { ref } from 'vue'

export function useDialog(initialVisible = false) {
  const visible = ref(initialVisible)
  const open = () => { visible.value = true }
  const close = () => { visible.value = false }
  return { visible, open, close }
}
