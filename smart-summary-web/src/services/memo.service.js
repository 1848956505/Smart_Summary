import http from './http'

export const memoService = {
  listFolders() {
    return http.get('/api/memo/folders')
  },
  listWeeks(folderId) {
    return http.get('/api/memo/weeks', { params: { folderId } })
  },
  getWeek(id) {
    return http.get(`/api/memo/weeks/${id}`)
  },
  listFragments(weekRecordId) {
    return http.get('/api/memo/fragments', { params: { weekRecordId } })
  }
}
