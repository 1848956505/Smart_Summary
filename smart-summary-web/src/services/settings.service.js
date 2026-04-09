import http from './http'

export const settingsService = {
  get() {
    const userStr = localStorage.getItem('user')
    const user = userStr ? JSON.parse(userStr) : null
    return http.get('/api/settings', { params: { userId: user?.id } })
  },
  save(payload) {
    return http.post('/api/settings', payload)
  },
  changePassword(payload) {
    return http.post('/api/settings/password', payload)
  },
  testConnection(payload) {
    return http.post('/api/settings/test-connection', payload)
  }
}
