import http from './http'

export const summaryService = {
  generate(payload) {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    return http.post('/api/generate', { ...payload, userId: user?.id })
  },
  listHistory() {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    return http.get('/api/history', { params: { userId: user?.id } })
  },
  deleteHistory(id) {
    return http.delete(`/api/history/${id}`)
  }
}
