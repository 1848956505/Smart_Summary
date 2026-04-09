import axios from 'axios'

const http = axios.create({
  timeout: 30000
})

http.interceptors.request.use((config) => {
  const userStr = localStorage.getItem('user')
  const user = userStr ? JSON.parse(userStr) : null
  const headers = config.headers || {}
  if (user?.id) {
    headers['X-User-Id'] = String(user.id)
  }
  config.headers = headers
  return config
})

export default http
