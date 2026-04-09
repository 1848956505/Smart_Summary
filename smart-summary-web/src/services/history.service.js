import http from './http'

export const historyService = {
  list() {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    return http.get('/api/history', { params: { userId: user?.id } })
  },
  remove(id) {
    return http.delete(`/api/history/${id}`)
  }
}
