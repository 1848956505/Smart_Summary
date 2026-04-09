import { computed, ref } from 'vue'

export function usePagination(defaultPageSize = 10) {
  const page = ref(1)
  const pageSize = ref(defaultPageSize)
  const setPage = (value) => { page.value = value }
  const setPageSize = (value) => { pageSize.value = value }
  const offset = computed(() => (page.value - 1) * pageSize.value)
  return { page, pageSize, offset, setPage, setPageSize }
}
