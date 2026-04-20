<template>
  <div class="history-page app-page-shell">
    <div class="history-page__toolbar app-surface">
      <div class="history-page__toolbar-copy">
        <p class="history-page__eyebrow">HISTORY</p>
        <h2 class="app-title">历史阅读台</h2>
        <p class="app-subtitle">回看、检索并复用已经生成过的周报内容。</p>
      </div>

      <div class="history-page__filters">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索标题、输入内容或周报内容"
          class="history-page__control history-page__search"
        />
        <div class="app-segmented app-segmented--compact history-page__segmented">
          <button
            v-for="option in historyStyleOptions"
            :key="option.value || 'all'"
            type="button"
            :class="['app-segmented__option', { 'is-active': styleFilter === option.value }]"
            @click="styleFilter = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="history-page__layout">
      <section class="history-page__rail app-surface">
        <div class="history-page__rail-header">
          <div>
            <p class="history-page__section-label">INDEX</p>
            <h3>周报记录</h3>
          </div>
          <span class="memo-chip memo-chip--accent">{{ filteredRecords.length }} 条</span>
        </div>

        <div class="history-page__list scroll-area">
          <button
            v-for="record in filteredRecords"
            :key="record.id"
            class="history-index"
            :class="{ 'history-index--active': selectedId === record.id }"
            @click="selectedId = record.id"
          >
            <div class="history-index__meta">
              <span :class="['memo-chip', styleChipClass(record.style)]">
                {{ styleLabel(record.style) }}
              </span>
              <span class="history-index__time">{{ formatTime(record.createTime) }}</span>
            </div>
            <p class="history-index__title">{{ historyTitle(record) }}</p>
            <p class="history-index__preview">{{ truncate(record.summaryText || record.originalText, 84) }}</p>
          </button>

          <AppEmpty v-if="!filteredRecords.length" description="没有符合条件的历史记录" />
        </div>
      </section>

      <section class="history-page__stage app-surface">
        <div v-if="currentRecord" class="history-page__stage-shell">
          <div class="history-page__meta-bar">
            <div class="history-page__meta">
              <span :class="['memo-chip', styleChipClass(currentRecord.style)]">{{ styleLabel(currentRecord.style) }}</span>
              <span class="memo-chip memo-chip--content">{{ currentRecord.modelId || '默认模型' }}</span>
              <span class="memo-chip memo-chip--soft">{{ formatTime(currentRecord.createTime) }}</span>
            </div>

            <div class="history-page__actions">
              <button class="memo-button memo-button--ghost" type="button" @click="copyCurrent">复制</button>
              <button class="memo-button memo-button--ghost" type="button" @click="exportCurrentMarkdown">Markdown</button>
              <button class="memo-button memo-button--ghost history-page__danger" type="button" @click="deleteCurrent">删除</button>
            </div>
          </div>

          <div class="history-page__document scroll-area">
            <section class="history-page__block">
              <div class="history-page__block-head">
                <p class="history-page__section-label">INPUT</p>
                <span class="memo-chip memo-chip--soft">原始输入</span>
              </div>
              <p class="history-page__plain">{{ currentRecord.originalText }}</p>
            </section>

            <section class="history-page__block history-page__block--report">
              <div class="history-page__block-head">
                <p class="history-page__section-label">REPORT</p>
                <span class="memo-chip memo-chip--accent">生成周报</span>
              </div>
              <div class="history-page__report" v-html="renderedSummary"></div>
            </section>
          </div>
        </div>

        <div v-else class="history-page__empty">
          <AppEmpty description="请选择一条历史记录查看详情" />
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { marked } from 'marked'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppEmpty from '@/components/ui/AppEmpty.vue'
import { getStyleLabel, normalizeStyle } from '@/components/common/themeConfig'
import { summaryService } from '@/services/summary.service'

const records = ref([])
const keyword = ref('')
const styleFilter = ref('')
const selectedId = ref(null)
const historyStyleOptions = [
  { label: '全部', value: '' },
  { label: '列表', value: 'list' },
  { label: '表格', value: 'table' }
]

const loadRecords = async () => {
  try {
    const { data } = await summaryService.listHistory()
    if (data.success) {
      records.value = data.data || []
      selectedId.value = records.value[0]?.id || null
    }
  } catch {
    records.value = []
  }
}

const filteredRecords = computed(() => records.value.filter((record) => {
  const source = [record.originalText, record.summaryText, historyTitle(record)].join(' ')
  const matchKeyword = !keyword.value || source.includes(keyword.value)
  const matchStyle = !styleFilter.value || normalizeStyle(record.style) === styleFilter.value
  return matchKeyword && matchStyle
}))

const currentRecord = computed(() => filteredRecords.value.find((item) => item.id === selectedId.value) || filteredRecords.value[0] || null)
const renderedSummary = computed(() => (currentRecord.value?.summaryText ? marked.parse(currentRecord.value.summaryText) : ''))

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const truncate = (text, limit) => {
  const value = text || ''
  return value.length > limit ? `${value.slice(0, limit)}...` : value
}

const styleLabel = (style) => getStyleLabel(style)

const styleChipClass = (style) => {
  return normalizeStyle(style) === 'table' ? 'memo-chip--info' : 'memo-chip--accent'
}

const historyTitle = (record) => {
  const source = record?.originalText || record?.summaryText || '未命名周报'
  return truncate(source.replace(/\s+/g, ' ').trim(), 34)
}

const copyCurrent = async () => {
  if (!currentRecord.value) return
  await navigator.clipboard.writeText(currentRecord.value.summaryText || '')
  ElMessage.success('已复制')
}

const exportCurrentMarkdown = () => {
  if (!currentRecord.value) return
  const blob = new Blob([currentRecord.value.summaryText || ''], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `history_${currentRecord.value.id}.md`
  a.click()
  URL.revokeObjectURL(url)
}

const deleteCurrent = async () => {
  if (!currentRecord.value) return
  try {
    await ElMessageBox.confirm('确认删除这条历史记录吗？', '提示', { type: 'warning' })
    await summaryService.deleteHistory(currentRecord.value.id)
    ElMessage.success('已删除')
    await loadRecords()
  } catch {
    // cancelled
  }
}

onMounted(loadRecords)
</script>

<style scoped>
.history-page {
  gap: var(--app-space-4);
  flex: 1;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  overflow: hidden;
}

.history-page__toolbar,
.history-page__rail,
.history-page__stage {
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid var(--memo-border);
  border-radius: var(--app-radius-2xl);
}

.history-page__toolbar {
  padding: 14px 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  box-shadow: 0 14px 34px rgba(39, 72, 124, 0.06);
}

.history-page__eyebrow,
.history-page__section-label {
  margin: 0 0 6px;
  font-size: 10px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.history-page__toolbar-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-page__filters {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.history-page__search {
  width: 300px;
}

.history-page__control :deep(.el-input__wrapper) {
  min-height: 32px;
  border-radius: 12px;
  box-shadow: none;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid var(--memo-button-border);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.history-page__control :deep(.el-select__wrapper.is-focused),
.history-page__control :deep(.el-input__wrapper.is-focus) {
  border-color: var(--memo-border-strong);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.history-page__segmented {
  flex-shrink: 0;
}

.history-page__layout {
  display: grid;
  grid-template-columns: minmax(280px, 0.28fr) minmax(0, 0.72fr);
  gap: var(--app-space-4);
  flex: 1;
  min-height: 0;
  height: 0;
  overflow: hidden;
}

.history-page__rail,
.history-page__stage {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.history-page__rail {
  padding: 14px 14px 12px;
  box-shadow: 0 12px 28px rgba(39, 72, 124, 0.05);
}

.history-page__rail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 14px;
  padding-inline: 2px;
}

.history-page__rail-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.history-page__list {
  flex: 1 1 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  height: 0;
  padding-right: 4px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  overscroll-behavior: contain;
}

.history-index {
  position: relative;
  flex: 0 0 auto;
  padding: 8px 11px;
  border-radius: 18px;
  border: 1px solid var(--memo-border);
  background: rgba(255, 255, 255, 0.94);
  text-align: left;
  overflow: hidden;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.history-index::before {
  content: '';
  position: absolute;
  inset: 12px auto 12px 0;
  width: 3px;
  border-radius: 999px;
  background: transparent;
  transition: background-color 0.2s ease;
}

.history-index:hover,
.history-index--active {
  border-color: var(--memo-border-strong);
  box-shadow: var(--memo-selected-shadow);
  background: linear-gradient(180deg, rgba(239, 246, 255, 0.94), rgba(232, 241, 255, 0.88));
  transform: translateY(-1px);
}

.history-index:hover::before,
.history-index--active::before {
  background: var(--app-color-primary);
}

.history-index__meta,
.history-page__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  flex-wrap: wrap;
}

.history-index__time {
  font-size: 11px;
  color: var(--app-color-text-muted);
  font-variant-numeric: tabular-nums;
}

.history-index__title {
  margin: 6px 0 3px;
  color: var(--app-color-text-strong);
  font-size: 13px;
  font-weight: 500;
  line-height: 1.5;
}

.history-index__preview {
  color: var(--app-color-text-soft);
  line-height: 1.5;
  font-size: 12px;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.history-page__stage {
  padding: 14px;
  box-shadow: 0 14px 34px rgba(39, 72, 124, 0.06);
}

.history-page__stage-shell {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
  flex: 1;
  overflow: hidden;
}

.history-page__meta-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 14px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(246, 250, 255, 0.9));
  border: 1px solid var(--memo-border);
  box-shadow: 0 10px 24px rgba(39, 72, 124, 0.05);
}

.history-page__actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.history-page__danger {
  color: var(--app-color-danger);
}

.history-page__danger:hover {
  color: var(--app-color-danger);
  border-color: rgba(209, 67, 67, 0.18);
  background: rgba(255, 244, 244, 0.98);
}

.history-page__document {
  flex: 1 1 0;
  min-height: 0;
  height: 0;
  padding-right: 8px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  overflow-x: hidden;
  scrollbar-gutter: stable;
  overscroll-behavior: contain;
}

.history-page__block {
  padding: 18px 20px;
  border-radius: 20px;
  border: 1px solid var(--memo-border);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(248, 251, 255, 0.9));
  box-shadow: 0 10px 24px rgba(39, 72, 124, 0.04);
}

.history-page__block--report {
  flex: none;
  min-height: auto;
}

.history-page__block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 14px;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(84, 112, 161, 0.1);
}

.history-page__plain,
.history-page__report {
  color: var(--app-color-text);
  line-height: 1.85;
}

.history-page__plain {
  white-space: pre-wrap;
  margin: 0;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(245, 249, 255, 0.72);
  border: 1px solid rgba(84, 112, 161, 0.08);
}

.history-page__report {
  overflow-x: auto;
  max-width: 100%;
  padding-right: 2px;
}

.history-page__report :deep(h1) {
  font-size: 24px;
  margin: 0 0 14px;
  letter-spacing: -0.02em;
}

.history-page__report :deep(h2) {
  font-size: 19px;
  margin: 22px 0 10px;
  letter-spacing: -0.01em;
}

.history-page__report :deep(h3) {
  font-size: 16px;
  margin: 18px 0 8px;
}

.history-page__report :deep(p),
.history-page__report :deep(li) {
  line-height: 1.85;
}

.history-page__report :deep(ul),
.history-page__report :deep(ol) {
  padding-left: 1.4em;
}

.history-page__report :deep(blockquote) {
  margin: 14px 0;
  padding: 12px 14px;
  border-left: 3px solid rgba(59, 130, 246, 0.28);
  border-radius: 0 14px 14px 0;
  background: rgba(243, 248, 255, 0.9);
  color: var(--app-color-text-soft);
}

.history-page__report :deep(code) {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(236, 243, 255, 0.96);
  color: var(--app-color-text-strong);
  font-size: 0.92em;
}

.history-page__report :deep(pre) {
  overflow-x: auto;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(245, 249, 255, 0.96);
  border: 1px solid rgba(84, 112, 161, 0.1);
}

.history-page__report :deep(pre code) {
  padding: 0;
  background: transparent;
}

.history-page__report :deep(table) {
  width: max-content;
  min-width: 100%;
  border-collapse: collapse;
  margin: 14px 0 8px;
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 26px rgba(39, 72, 124, 0.06);
}

.history-page__report :deep(th),
.history-page__report :deep(td) {
  border: 1px solid rgba(84, 112, 161, 0.14);
  padding: 11px 13px;
  text-align: left;
  vertical-align: top;
  white-space: nowrap;
}

.history-page__report :deep(th) {
  background: linear-gradient(180deg, rgba(233, 242, 255, 0.95), rgba(226, 237, 255, 0.88));
  color: var(--app-color-text-strong);
  font-weight: 700;
}

.history-page__report :deep(tr:nth-child(even) td) {
  background: rgba(248, 251, 255, 0.72);
}

.history-page__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 1200px) {
  .history-page__toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .history-page__search,
  .history-page__select {
    width: 100%;
  }

  .history-page__layout {
    grid-template-columns: 1fr;
    grid-template-rows: minmax(0, 0.72fr) minmax(0, 1fr);
    height: 100%;
  }

  .history-page__rail,
  .history-page__stage {
    height: 100%;
    min-height: 0;
  }

  .history-page__list,
  .history-page__document {
    height: 0;
  }
}
</style>
