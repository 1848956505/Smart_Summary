import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export function useMessage() {
  const loading = ref(false)
  const success = (text) => ElMessage.success(text)
  const error = (text) => ElMessage.error(text)
  const warning = (text) => ElMessage.warning(text)
  return { loading, success, error, warning }
}
