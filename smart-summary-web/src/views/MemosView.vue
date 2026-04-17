<template>
  <div class="memo-workspace">
    <MemoSidebar
      :folders="folders"
      :weeks-by-folder="weeksByFolder"
      :selected-folder-id="selectedFolderId"
      :selected-week-id="selectedWeekId"
      @create-folder="openCreateFolderDialog"
      @toggle-folder="handleToggleFolder"
      @select-folder="handleSelectFolder"
      @rename-folder="openEditFolderDialog"
      @delete-folder="handleDeleteFolder"
      @create-week="openCreateWeekDialog"
      @select-week="handleSelectWeek"
      @rename-week="openEditWeekDialog"
      @delete-week="handleDeleteWeek"
    />

    <section class="memo-workspace__content">
      <WeekRecordHeader
        :current-week="currentWeek"
        :stats="stats"
        :generating="generating"
        @generate="handleGenerateSummary"
        @save="handleSaveSummary"
        @copy="handleCopySummary"
        @export-markdown="handleExportMarkdown"
        @export-pdf="handleExportPdf"
        @archive="handleArchive"
        @open-stats="statsDrawerVisible = true"
      />

      <div v-if="currentWeek" class="memo-workspace__filters">
        <el-select v-model="filters.status" size="small" style="width: 130px">
          <el-option label="全部状态" value="all" />
          <el-option label="待办" value="todo" />
          <el-option label="进行中" value="doing" />
          <el-option label="已完成" value="done" />
          <el-option label="阻塞" value="blocked" />
        </el-select>
        <el-select v-model="filters.tag" size="small" style="width: 150px">
          <el-option label="全部标签" value="all" />
          <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
        <el-input v-model="filters.keyword" size="small" clearable placeholder="搜索标题或内容" style="width: 240px" />
        <el-select v-model="activeDate" size="small" style="width: 130px" @change="handleSelectDate">
          <el-option
            v-for="day in weekNavigationOptions"
            :key="day.date"
            :label="day.label"
            :value="day.date"
          />
        </el-select>
        <el-button size="small" text @click="jumpToDefaultDate">
          <el-icon><Calendar /></el-icon>
          默认
        </el-button>
        <el-button size="small" text @click="recordsCollapsed = !recordsCollapsed">
          <el-icon><Fold v-if="!recordsCollapsed" /><Expand v-else /></el-icon>
          {{ recordsCollapsed ? '展开' : '收起' }}
        </el-button>
      </div>

      <div v-if="currentWeek" class="memo-workspace__body">
        <div v-show="!recordsCollapsed" class="memo-workspace__records-shell">
          <DailyFragmentList
            :fragments="fragments"
            :week-start-date="currentWeek.weekStartDate"
            :week-end-date="currentWeek.weekEndDate"
            :active-date="activeDate"
            :status-filter="filters.status"
            :tag-filter="filters.tag"
            :keyword="filters.keyword"
            @edit-fragment="openEditFragmentDialog"
            @delete-fragment="handleDeleteFragment"
            @move-up="handleMoveUp"
            @move-down="handleMoveDown"
            @reorder-day="handleReorderDay"
            @select-date="handleSelectDate"
          />
        </div>
        <div v-if="recordsCollapsed" class="memo-workspace__collapsed">
          <el-empty description="记录已收起">
            <el-button type="primary" plain @click="recordsCollapsed = false">展开记录</el-button>
          </el-empty>
        </div>
      </div>

      <MemoQuickComposer
        v-if="currentWeek"
        v-model="quickText"
        :active-date="activeDate"
        placeholder="记下此刻的工作碎片..."
        @submit="handleQuickSubmit"
        @open-detail="openCreateFragmentDialog(activeDate)"
        @jump-today="jumpToDefaultDate"
      />

      <div v-else class="memo-workspace__empty">
        <el-empty description="请选择或创建周记录" :image-size="88">
          <el-button type="primary" @click="openCreateFolderDialog">新建文件夹</el-button>
        </el-empty>
      </div>
    </section>

    <MemoFolderDialog
      v-model:visible="folderDialog.visible"
      :mode="folderDialog.mode"
      :loading="folderDialog.loading"
      :model-value="folderDialog.draft"
      @submit="submitFolderDialog"
    />

    <MemoWeekDialog
      v-model:visible="weekDialog.visible"
      :mode="weekDialog.mode"
      :loading="weekDialog.loading"
      :folders="folders"
      :model-value="weekDialog.draft"
      @submit="submitWeekDialog"
    />

    <MemoFragmentDialog
      v-model:visible="fragmentDialog.visible"
      :mode="fragmentDialog.mode"
      :loading="fragmentDialog.loading"
      :model-value="fragmentDialog.draft"
      @submit="submitFragmentDialog"
    />

    <el-drawer
      v-model="statsDrawerVisible"
      title="本周统计"
      size="420px"
      append-to-body
      :with-header="true"
    >
      <WeeklyStatsPanel :fragments="fragments" />
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Calendar, Fold, Expand } from '@element-plus/icons-vue'
import axios from 'axios'
import html2pdf from 'html2pdf.js'
import MemoSidebar from '@/components/memo/MemoSidebar.vue'
import WeekRecordHeader from '@/components/memo/WeekRecordHeader.vue'
import DailyFragmentList from '@/components/memo/DailyFragmentList.vue'
import WeeklyStatsPanel from '@/components/memo/WeeklyStatsPanel.vue'
import MemoQuickComposer from '@/components/memo/MemoQuickComposer.vue'
import MemoFolderDialog from '@/components/memo/MemoFolderDialog.vue'
import MemoWeekDialog from '@/components/memo/MemoWeekDialog.vue'
import MemoFragmentDialog from '@/components/memo/MemoFragmentDialog.vue'

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
const recordsCollapsed = ref(false)
const activeDate = ref('')
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
  for (const f of fragments.value) {
    result.total += 1
    if (result[f.status] !== undefined) result[f.status] += 1
  }
  return result
})

const availableTags = computed(() => {
  const tags = new Set()
  for (const f of fragments.value) {
    if (f.tag) tags.add(f.tag)
  }
  return Array.from(tags)
})

const weekNavigationOptions = computed(() => buildWeekDayItems(currentWeek.value))

const syncActiveDate = () => {
  activeDate.value = getDefaultWeekDate(currentWeek.value)
}

const handleSelectDate = async (date) => {
  activeDate.value = date
  await nextTick()
  jumpToDate(date)
}

const jumpToDate = async (date) => {
  if (!date) return
  const target = document.getElementById(`memo-day-${date}`)
  if (target) {
    target.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const jumpToDefaultDate = async () => {
  const targetDate = getDefaultWeekDate(currentWeek.value)
  activeDate.value = targetDate
  await nextTick()
  jumpToDate(targetDate)
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

    const storedWeekId = Number(localStorage.getItem('memo_selected_week_id') || 0)
    if (storedWeekId) {
      for (const folder of folders.value) {
        const weeks = weeksByFolder[folder.id] || []
        const found = weeks.find((w) => w.id === storedWeekId)
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
  fragments.value = data.success ? (data.data || []).sort((a, b) => {
    const dateOrder = String(a.workDate || '').localeCompare(String(b.workDate || ''))
    if (dateOrder !== 0) return dateOrder
    return (a.sortOrder || 0) - (b.sortOrder || 0)
  }) : []
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
  jumpToDate(activeDate.value)
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
    .filter((f) => (f.workDate || '').slice(0, 10) === date)
    .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
  const byId = Object.fromEntries(sameDay.map((f) => [f.id, f]))

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

const formatLocalDate = (date) => {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}

const buildWeekDayItems = (week) => {
  if (!week?.weekStartDate) return []
  const start = new Date(week.weekStartDate)
  if (Number.isNaN(start.getTime())) return []
  const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const prefixes = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
  return Array.from({ length: 7 }).map((_, idx) => {
    const d = new Date(start)
    d.setDate(start.getDate() + idx)
    return {
      date: formatLocalDate(d),
      label: labels[idx],
      prefix: prefixes[idx]
    }
  })
}

const getDefaultWeekDate = (week) => {
  const items = buildWeekDayItems(week)
  if (!items.length) {
    return formatLocalDate(new Date())
  }
  const weekdayIndex = (new Date().getDay() + 6) % 7
  return items[weekdayIndex]?.date || items[0].date
}

const getDefaultWeekRange = () => {
  const now = new Date()
  const day = now.getDay() || 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - day + 1)
  const sunday = new Date(monday)
  sunday.setDate(monday.getDate() + 6)
  return {
    weekStartDate: formatLocalDate(monday),
    weekEndDate: formatLocalDate(sunday)
  }
}

const nextFolderSortOrder = () => {
  const last = [...folders.value].sort((a, b) => (b.sortOrder || 0) - (a.sortOrder || 0))[0]
  return (last?.sortOrder || 0) + 1
}

const nextFragmentSortOrder = (date) => {
  const sameDay = fragments.value.filter((f) => (f.workDate || '').slice(0, 10) === date)
  const last = sameDay.sort((a, b) => (b.sortOrder || 0) - (a.sortOrder || 0))[0]
  return (last?.sortOrder || 0) + 1
}

const swapSortOrder = async (fragment, direction) => {
  const date = (fragment.workDate || '').slice(0, 10)
  const sameDay = fragments.value
    .filter((f) => (f.workDate || '').slice(0, 10) === date)
    .sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))

  const index = sameDay.findIndex((f) => f.id === fragment.id)
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
</script>

<style scoped>
.memo-workspace {
  display: flex;
  gap: 18px;
  min-height: 100%;
  height: calc(100% + var(--app-space-6) * 2);
  width: calc(100% + var(--app-space-6) * 2);
  margin: calc(var(--app-space-6) * -1);
  overflow: hidden;
}

.memo-workspace__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
  overflow: hidden;
}

.memo-workspace__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 2px;
}

.memo-workspace__body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  flex: 1;
  align-items: stretch;
  overflow: hidden;
}

.memo-workspace__records-shell {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-right: 4px;
}

.memo-workspace__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

@media (max-width: 1300px) {
  .memo-workspace {
    flex-direction: column;
    overflow: hidden;
  }
}

@media (max-width: 1100px) {
  .memo-workspace__body {
    flex-direction: column;
  }
}

.memo-workspace__content :deep(.memo-composer) {
  margin-top: 2px;
}
</style>
