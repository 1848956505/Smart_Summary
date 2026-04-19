import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import html2pdf from 'html2pdf.js'
import { buildWeekDayItems, formatLocalDate, getDefaultWeekDate, getDefaultWeekRange } from './memoDateUtils'

const today = () => formatLocalDate(new Date())

const includesDate = (weekRecord, date) => {
  if (!weekRecord?.weekStartDate || !weekRecord?.weekEndDate || !date) return false
  return weekRecord.weekStartDate <= date && weekRecord.weekEndDate >= date
}

export function useMemoWorkspace() {
  const folders = ref([])
  const weeksByFolder = reactive({})
  const selectedFolderId = ref(null)
  const selectedWeekId = ref(null)
  const currentWeek = ref(null)
  const fragments = ref([])
  const summaryContent = ref('')
  const quickText = ref('')
  const generating = ref(false)
  const statsDrawerVisible = ref(false)
  const sidebarCollapsed = ref(false)
  const activeDate = ref('')
  const recordsShellRef = ref(null)

  const filters = reactive({
    status: 'all',
    tag: 'all',
    keyword: ''
  })

  const folderDialog = reactive({
    visible: false,
    loading: false,
    mode: 'create',
    draft: {}
  })

  const weekDialog = reactive({
    visible: false,
    loading: false,
    mode: 'create',
    draft: {}
  })

  const fragmentDialog = reactive({
    visible: false,
    loading: false,
    mode: 'create',
    draft: {}
  })

  const router = useRouter()

  const user = computed(() => {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  })

  const memoApi = computed(() => {
    const userId = user.value?.id
    return {
      headers: {
        'X-User-Id': String(userId || '')
      }
    }
  })

  const stats = computed(() => {
    const result = { total: 0, todo: 0, doing: 0, done: 0, blocked: 0 }
    for (const fragment of fragments.value) {
      result.total += 1
      if (result[fragment.status] !== undefined) result[fragment.status] += 1
    }
    return result
  })

  const availableTags = computed(() => {
    const tags = new Set()
    for (const fragment of fragments.value) {
      if (fragment.tag) tags.add(fragment.tag)
    }
    return Array.from(tags)
  })

  const weekNavigationOptions = computed(() => buildWeekDayItems(currentWeek.value))

  const syncActiveDate = () => {
    activeDate.value = getDefaultWeekDate(currentWeek.value)
  }

  const jumpToDate = async (date) => {
    if (!date) return
    const shell = recordsShellRef.value
    const target = document.getElementById(`memo-day-${date}`)
    if (!shell || !target) return
    requestAnimationFrame(() => {
      const top = Math.max(target.offsetTop - 8, 0)
      shell.scrollTo({ top, behavior: 'smooth' })
    })
  }

  const handleSelectDate = async (date) => {
    activeDate.value = date
    await nextTick()
    await jumpToDate(date)
  }

  const jumpToDefaultDate = async () => {
    const targetDate = getDefaultWeekDate(currentWeek.value)
    activeDate.value = targetDate
    await nextTick()
    await jumpToDate(targetDate)
  }

  onMounted(async () => {
    if (!user.value?.id) return
    await loadFolders()
  })

  const loadFolders = async () => {
    try {
      const { data } = await axios.get('/api/memo/folders', memoApi.value)
      if (!data.success) {
        ElMessage.error(data.message || '加载文件夹失败')
        return
      }
      folders.value = (data.data || []).sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))

      for (const key of Object.keys(weeksByFolder)) {
        delete weeksByFolder[key]
      }

      for (const folder of folders.value) {
        await loadWeeks(folder.id)
      }

      const currentDate = today()
      for (const folder of folders.value) {
        const weeks = weeksByFolder[folder.id] || []
        const currentWeekMatch = weeks.find((week) => includesDate(week, currentDate))
        if (currentWeekMatch) {
          await handleSelectWeek(currentWeekMatch)
          return
        }
      }

      const storedWeekId = Number(localStorage.getItem('memo_selected_week_id') || 0)
      if (storedWeekId) {
        for (const folder of folders.value) {
          const weeks = weeksByFolder[folder.id] || []
          const found = weeks.find((week) => week.id === storedWeekId)
          if (found) {
            await handleSelectWeek(found)
            return
          }
        }
      }

      if (!selectedFolderId.value && folders.value.length) {
        selectedFolderId.value = folders.value[0].id
      }

      if (!selectedWeekId.value) {
        for (const folder of folders.value) {
          const weekRecords = weeksByFolder[folder.id] || []
          if (weekRecords.length) {
            await handleSelectWeek(weekRecords[0])
            break
          }
        }
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '加载文件夹失败')
    }
  }

  const loadWeeks = async (folderId) => {
    try {
      const { data } = await axios.get('/api/memo/weeks', {
        ...memoApi.value,
        params: { folderId }
      })
      weeksByFolder[folderId] = data.success ? (data.data || []) : []
    } catch {
      weeksByFolder[folderId] = []
    }
  }

  const loadWeekDetail = async (weekRecordId) => {
    const { data } = await axios.get(`/api/memo/weeks/${weekRecordId}`, memoApi.value)
    if (!data.success) return
    currentWeek.value = data.data
    summaryContent.value = data.data.summaryContent || ''
  }

  const loadFragments = async (weekRecordId) => {
    const { data } = await axios.get('/api/memo/fragments', {
      ...memoApi.value,
      params: { weekRecordId }
    })
    fragments.value = data.success
      ? (data.data || []).sort((a, b) => {
          const dateOrder = String(a.workDate || '').localeCompare(String(b.workDate || ''))
          if (dateOrder !== 0) return dateOrder
          return (a.sortOrder || 0) - (b.sortOrder || 0)
        })
      : []
  }

  const handleSelectFolder = (folder) => {
    selectedFolderId.value = folder.id
  }

  const handleToggleFolder = async (folder) => {
    await axios.put(`/api/memo/folders/${folder.id}`, {
      isCollapsed: folder.isCollapsed ? 0 : 1
    }, memoApi.value)
    await loadFolders()
  }

  const openCreateFolderDialog = () => {
    folderDialog.mode = 'create'
    folderDialog.draft = {
      name: '新建文件夹',
      sortOrder: nextFolderSortOrder(),
      isCollapsed: 0
    }
    folderDialog.visible = true
  }

  const openEditFolderDialog = (folder) => {
    folderDialog.mode = 'edit'
    folderDialog.draft = { ...folder }
    folderDialog.visible = true
  }

  const submitFolderDialog = async (payload) => {
    folderDialog.loading = true
    try {
      if (folderDialog.mode === 'edit') {
        const { data } = await axios.put(`/api/memo/folders/${folderDialog.draft.id}`, payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '文件夹更新失败')
          return
        }
        ElMessage.success('文件夹已更新')
      } else {
        const { data } = await axios.post('/api/memo/folders', payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '文件夹创建失败')
          return
        }
        ElMessage.success('文件夹创建成功')
        selectedFolderId.value = data.data?.id || selectedFolderId.value
      }
      folderDialog.visible = false
      await loadFolders()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '文件夹操作失败')
    } finally {
      folderDialog.loading = false
    }
  }

  const handleDeleteFolder = async (folder) => {
    await ElMessageBox.confirm(`确认删除文件夹「${folder.name}」及其全部周记录？`, '提示', { type: 'warning' })
    await axios.delete(`/api/memo/folders/${folder.id}`, memoApi.value)
    if (selectedFolderId.value === folder.id) {
      selectedFolderId.value = null
      selectedWeekId.value = null
      currentWeek.value = null
      fragments.value = []
      summaryContent.value = ''
      quickText.value = ''
      activeDate.value = ''
      localStorage.removeItem('memo_selected_week_id')
    }
    await loadFolders()
    ElMessage.success('文件夹已删除')
  }

  const openCreateWeekDialog = (folderId) => {
    const { weekStartDate, weekEndDate } = getDefaultWeekRange()
    weekDialog.mode = 'create'
    weekDialog.draft = {
      folderId: folderId || selectedFolderId.value || folders.value[0]?.id || null,
      title: `${weekStartDate}~${weekEndDate} 工作周报`,
      weekStartDate,
      weekEndDate,
      status: 'draft',
      summaryContent: ''
    }
    weekDialog.visible = true
  }

  const openEditWeekDialog = (weekRecord) => {
    weekDialog.mode = 'edit'
    weekDialog.draft = { ...weekRecord }
    weekDialog.visible = true
  }

  const submitWeekDialog = async (payload) => {
    weekDialog.loading = true
    try {
      if (weekDialog.mode === 'edit') {
        const { data } = await axios.put(`/api/memo/weeks/${weekDialog.draft.id}`, payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '周记录更新失败')
          return
        }
        ElMessage.success('周记录已更新')
      } else {
        const { data } = await axios.post('/api/memo/weeks', payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '周记录创建失败')
          return
        }
        ElMessage.success('周记录创建成功')
        await handleSelectWeek(data.data)
      }
      weekDialog.visible = false
      await refreshWeekListMeta()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '周记录操作失败')
    } finally {
      weekDialog.loading = false
    }
  }

  const handleCreateWeek = async (folderId) => {
    openCreateWeekDialog(folderId)
  }

  const handleRenameWeek = async (weekRecord) => {
    openEditWeekDialog(weekRecord)
  }

  const handleDeleteWeek = async (weekRecord) => {
    await ElMessageBox.confirm(`确认删除周记录「${weekRecord.title}」及其全部碎片？`, '提示', { type: 'warning' })
    await axios.delete(`/api/memo/weeks/${weekRecord.id}`, memoApi.value)

    if (selectedWeekId.value === weekRecord.id) {
      selectedWeekId.value = null
      currentWeek.value = null
      fragments.value = []
      summaryContent.value = ''
      quickText.value = ''
      activeDate.value = ''
      localStorage.removeItem('memo_selected_week_id')
    }

    await refreshWeekListMeta()
    ElMessage.success('周记录已删除')
  }

  const handleSelectWeek = async (weekRecord) => {
    selectedWeekId.value = weekRecord.id
    selectedFolderId.value = weekRecord.folderId
    localStorage.setItem('memo_selected_week_id', String(weekRecord.id))
    await loadWeekDetail(weekRecord.id)
    await loadFragments(weekRecord.id)
    syncActiveDate()
    await nextTick()
    await jumpToDate(activeDate.value)
  }

  const openCreateFragmentDialog = (date) => {
    if (!selectedWeekId.value) return
    const targetDate = date || activeDate.value || currentWeek.value?.weekStartDate || formatLocalDate(new Date())
    fragmentDialog.mode = 'create'
    fragmentDialog.draft = {
      weekRecordId: selectedWeekId.value,
      workDate: targetDate,
      title: '',
      content: '',
      status: 'todo',
      priority: 'medium',
      tag: '未分类',
      sortOrder: nextFragmentSortOrder(targetDate)
    }
    fragmentDialog.visible = true
  }

  const openEditFragmentDialog = (fragment) => {
    fragmentDialog.mode = 'edit'
    fragmentDialog.draft = { ...fragment }
    fragmentDialog.visible = true
  }

  const submitFragmentDialog = async (payload) => {
    fragmentDialog.loading = true
    try {
      if (fragmentDialog.mode === 'edit') {
        const { data } = await axios.put(`/api/memo/fragments/${fragmentDialog.draft.id}`, payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '碎片更新失败')
          return
        }
        ElMessage.success('碎片已更新')
      } else {
        const { data } = await axios.post('/api/memo/fragments', payload, memoApi.value)
        if (!data.success) {
          ElMessage.error(data.message || '碎片创建失败')
          return
        }
        ElMessage.success('碎片创建成功')
      }
      fragmentDialog.visible = false
      await loadFragments(selectedWeekId.value)
      await refreshWeekListMeta()
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '碎片操作失败')
    } finally {
      fragmentDialog.loading = false
    }
  }

  const handleQuickSubmit = async (text) => {
    if (!selectedWeekId.value) return
    const date = activeDate.value || currentWeek.value?.weekStartDate || formatLocalDate(new Date())
    await axios.post('/api/memo/fragments', {
      weekRecordId: selectedWeekId.value,
      workDate: date,
      title: text,
      content: '',
      status: 'done',
      priority: 'medium',
      tag: '未分类',
      sortOrder: nextFragmentSortOrder(date)
    }, memoApi.value)
    quickText.value = ''
    await loadFragments(selectedWeekId.value)
    await refreshWeekListMeta()
  }

  const handleDeleteFragment = async (id) => {
    await axios.delete(`/api/memo/fragments/${id}`, memoApi.value)
    await loadFragments(selectedWeekId.value)
    await refreshWeekListMeta()
  }

  const handleMoveUp = async (fragment) => {
    await swapSortOrder(fragment, -1)
  }

  const handleMoveDown = async (fragment) => {
    await swapSortOrder(fragment, 1)
  }

  const handleReorderDay = async ({ date, orderedIds }) => {
    const sameDay = fragments.value
      .filter((fragment) => (fragment.workDate || '').slice(0, 10) === date)
      .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
    const byId = Object.fromEntries(sameDay.map((fragment) => [fragment.id, fragment]))

    let changed = false
    for (let i = 0; i < orderedIds.length; i += 1) {
      const id = orderedIds[i]
      const fragment = byId[id]
      if (!fragment) continue
      const newOrder = i + 1
      if ((fragment.sortOrder || 0) !== newOrder) {
        changed = true
        await axios.put(`/api/memo/fragments/${id}`, { ...fragment, sortOrder: newOrder }, memoApi.value)
      }
    }

    if (changed) {
      await loadFragments(selectedWeekId.value)
    }
  }

  const handleGenerateSummary = async () => {
    if (!selectedWeekId.value) return
    if (!fragments.value.length) {
      ElMessage.warning('当前周没有碎片记录，无法生成周报')
      return
    }

    generating.value = true
    try {
      const { data } = await axios.post(`/api/memo/weeks/${selectedWeekId.value}/generate-summary`, {
        projectName: '毕设系统开发',
        userPosition: user.value?.position || '学生开发者'
      }, memoApi.value)
      if (!data.success) {
        ElMessage.error(data.message || '生成失败')
        return
      }
      summaryContent.value = data.data.summary || ''
      await loadWeekDetail(selectedWeekId.value)
      await refreshWeekListMeta()
      localStorage.setItem('smart-summary:generate-result', JSON.stringify({
        source: 'memo-week',
        title: currentWeek.value?.title || '周报生成结果',
        summary: data.data.summary || '',
        weekTitle: currentWeek.value?.title || '',
        weekRange: currentWeek.value ? `${currentWeek.value.weekStartDate} ~ ${currentWeek.value.weekEndDate}` : '',
        createdAt: new Date().toISOString()
      }))
      await router.push({ path: '/app/generate', query: { source: 'memo-week' } })
      ElMessage.success('周报生成成功，已跳转到智能生成页')
    } finally {
      generating.value = false
    }
  }

  const handleSaveSummary = async () => {
    if (!selectedWeekId.value) return
    await axios.post(`/api/memo/weeks/${selectedWeekId.value}/save-summary`, {
      summaryContent: summaryContent.value,
      status: 'generated'
    }, memoApi.value)
    await loadWeekDetail(selectedWeekId.value)
    await refreshWeekListMeta()
    ElMessage.success('周报已保存到历史记录')
  }

  const handleArchive = async () => {
    if (!selectedWeekId.value) return
    await axios.put(`/api/memo/weeks/${selectedWeekId.value}`, {
      status: 'archived',
      summaryContent: summaryContent.value
    }, memoApi.value)
    await loadWeekDetail(selectedWeekId.value)
    await refreshWeekListMeta()
    ElMessage.success('已归档')
  }

  const handleCopySummary = async () => {
    if (!summaryContent.value) return
    await navigator.clipboard.writeText(summaryContent.value)
    ElMessage.success('周报已复制')
  }

  const handleExportMarkdown = async () => {
    if (!selectedWeekId.value || !summaryContent.value) return
    const fileName = `weekly-summary-${selectedWeekId.value}.md`
    saveTextFile(fileName, summaryContent.value)
    ElMessage.success('Markdown 导出成功')
  }

  const handleExportPdf = async () => {
    if (!summaryContent.value) return
    const temp = document.createElement('div')
    temp.innerHTML = `<pre style="white-space: pre-wrap; font-family: Arial, sans-serif;">${escapeHtml(summaryContent.value)}</pre>`
    html2pdf().set({
      margin: 10,
      filename: `weekly-summary-${selectedWeekId.value}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }).from(temp).save()
    ElMessage.success('PDF 导出成功')
  }

  const refreshWeekListMeta = async () => {
    if (!selectedFolderId.value) return
    await loadWeeks(selectedFolderId.value)
    if (selectedWeekId.value) {
      await loadWeekDetail(selectedWeekId.value)
    }
  }

  const saveTextFile = (fileName, content) => {
    const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = fileName
    a.click()
    URL.revokeObjectURL(url)
  }

  const escapeHtml = (str) => {
    return str
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#039;')
  }

  const nextFolderSortOrder = () => {
    const last = [...folders.value].sort((a, b) => (b.sortOrder || 0) - (a.sortOrder || 0))[0]
    return (last?.sortOrder || 0) + 1
  }

  const nextFragmentSortOrder = (date) => {
    const sameDay = fragments.value.filter((fragment) => (fragment.workDate || '').slice(0, 10) === date)
    const last = sameDay.sort((a, b) => (b.sortOrder || 0) - (a.sortOrder || 0))[0]
    return (last?.sortOrder || 0) + 1
  }

  const swapSortOrder = async (fragment, direction) => {
    const date = (fragment.workDate || '').slice(0, 10)
    const sameDay = fragments.value
      .filter((item) => (item.workDate || '').slice(0, 10) === date)
      .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))

    const index = sameDay.findIndex((item) => item.id === fragment.id)
    const targetIndex = index + direction
    if (index < 0 || targetIndex < 0 || targetIndex >= sameDay.length) return

    const current = sameDay[index]
    const target = sameDay[targetIndex]
    const currentOrder = current.sortOrder || index + 1
    const targetOrder = target.sortOrder || targetIndex + 1

    await axios.put(`/api/memo/fragments/${current.id}`, { ...current, sortOrder: targetOrder }, memoApi.value)
    await axios.put(`/api/memo/fragments/${target.id}`, { ...target, sortOrder: currentOrder }, memoApi.value)
    await loadFragments(selectedWeekId.value)
  }

  return {
    folders,
    weeksByFolder,
    selectedFolderId,
    selectedWeekId,
    currentWeek,
    fragments,
    summaryContent,
    quickText,
    generating,
    statsDrawerVisible,
    sidebarCollapsed,
    activeDate,
    filters,
    folderDialog,
    weekDialog,
    fragmentDialog,
    recordsShellRef,
    stats,
    availableTags,
    weekNavigationOptions,
    user,
    memoApi,
    syncActiveDate,
    handleSelectDate,
    jumpToDate,
    jumpToDefaultDate,
    loadFolders,
    loadWeeks,
    loadWeekDetail,
    loadFragments,
    handleSelectFolder,
    handleToggleFolder,
    openCreateFolderDialog,
    openEditFolderDialog,
    submitFolderDialog,
    handleDeleteFolder,
    openCreateWeekDialog,
    openEditWeekDialog,
    submitWeekDialog,
    handleCreateWeek,
    handleRenameWeek,
    handleDeleteWeek,
    handleSelectWeek,
    openCreateFragmentDialog,
    openEditFragmentDialog,
    submitFragmentDialog,
    handleQuickSubmit,
    handleDeleteFragment,
    handleMoveUp,
    handleMoveDown,
    handleReorderDay,
    handleGenerateSummary,
    handleSaveSummary,
    handleArchive,
    handleCopySummary,
    handleExportMarkdown,
    handleExportPdf,
    refreshWeekListMeta
  }
}
