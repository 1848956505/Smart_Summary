<template>
  <div class="history-page app-page-shell">
    <div class="history-page__layout">
      <AppCard class="history-page__list-panel" compact>
        <template #header>
          <div>
            <p class="history-page__eyebrow">历史检索</p>
            <h2 class="app-title">历史周报</h2>
            <p class="app-subtitle">按记录浏览、筛选和定位周报内容。</p>
          </div>
          <AppTag type="primary">{{ records.length }} 条</AppTag>
        </template>

        <div class="history-page__filters">
          <el-input v-model="keyword" placeholder="搜索输入或输出内容" clearable />
          <el-select v-model="styleFilter" placeholder="风格筛选" clearable>
            <el-option label="全部" value="" />
            <el-option label="钉钉" value="dingtalk" />
            <el-option label="飞书" value="feishu" />
            <el-option label="企业微信" value="wechat" />
          </el-select>
        </div>

        <div class="history-page__list scroll-area">
          <button
            v-for="record in filteredRecords"
            :key="record.id"
            class="history-card"
            :class="{ 'history-card--active': selectedId === record.id }"
            @click="selectedId = record.id"
          >
            <div class="history-card__head">
              <span class="history-card__badge">{{ styleLabel(record.style) }}</span>
              <span class="history-card__time">{{ formatTime(record.createTime) }}</span>
            </div>
            <p class="history-card__title">{{ truncate(record.originalText, 80) }}</p>
            <p class="history-card__preview">{{ truncate(record.summaryText, 110) }}</p>
          </button>
        </div>
      </AppCard>

      <AppCard class="history-page__preview-panel" :compact="true">
        <template #header>
          <div>
            <p class="history-page__eyebrow">详情预览</p>
            <h2 class="app-title">记录详情</h2>
          </div>
          <div class="history-page__actions" v-if="currentRecord">
            <AppButton @click="copyCurrent">复制</AppButton>
            <AppButton @click="exportCurrentMarkdown">Markdown</AppButton>
            <AppButton @click="deleteCurrent" variant="danger">删除</AppButton>
          </div>
        </template>

        <div v-if="currentRecord" class="history-page__preview scroll-area">
          <div class="history-page__meta">
            <AppTag type="primary">{{ styleLabel(currentRecord.style) }}</AppTag>
            <AppTag>{{ currentRecord.modelId || '默认模型' }}</AppTag>
            <span class="history-page__meta-time">{{ formatTime(currentRecord.createTime) }}</span>
          </div>

          <section class="history-page__block">
            <h3>输入内容</h3>
            <p>{{ currentRecord.originalText }}</p>
          </section>

          <section class="history-page__block">
            <h3>输出内容</h3>
            <div class="history-page__summary" v-html="renderedSummary"></div>
          </section>
        </div>

        <AppEmpty v-else description="请选择一条历史记录查看详情" />
      </AppCard>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { marked } from 'marked'
import { ElMessage, ElMessageBox } from 'element-plus'
import AppCard from '@/components/ui/AppCard.vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppTag from '@/components/ui/AppTag.vue'
import AppEmpty from '@/components/ui/AppEmpty.vue'
import { summaryService } from '@/services/summary.service'

const records = ref([])
const keyword = ref('')
const styleFilter = ref('')
const selectedId = ref(null)

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
  const matchKeyword = !keyword.value || [record.originalText, record.summaryText].join(' ').includes(keyword.value)
  const matchStyle = !styleFilter.value || record.style === styleFilter.value
  return matchKeyword && matchStyle
}))

const currentRecord = computed(() => filteredRecords.value.find((item) => item.id === selectedId.value) || filteredRecords.value[0] || null)
const renderedSummary = computed(() => (currentRecord.value?.summaryText ? marked.parse(currentRecord.value.summaryText) : ''))

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const truncate = (text, limit) => {
  const value = text || ''
  return value.length > limit ? `${value.slice(0, limit)}...` : value
}

const styleLabel = (style) => {
  if (style === 'dingtalk') return '钉钉'
  if (style === 'feishu') return '飞书'
  return '企业微信'
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
    await summaryService.remove(currentRecord.value.id)
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
}

.history-page__layout {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: var(--app-space-4);
  min-height: 0;
}

.history-page__list-panel,
.history-page__preview-panel {
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.history-page__eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--app-color-text-muted);
}

.history-page__filters {
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 10px;
  margin-bottom: 14px;
}

.history-page__list {
  display: grid;
  gap: 12px;
  min-height: 0;
}

.history-card {
  padding: 14px;
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-color-border);
  background: var(--app-panel-bg-soft);
  text-align: left;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.history-card:hover,
.history-card--active {
  border-color: var(--app-color-primary);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.08);
  transform: translateY(-1px);
}

.history-card__head,
.history-page__meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.history-card__badge {
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  font-size: 12px;
  font-weight: 700;
}

.history-card__time,
.history-page__meta-time {
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.history-card__title {
  margin: 12px 0 6px;
  color: var(--app-color-text-strong);
  font-weight: 700;
  line-height: 1.5;
}

.history-card__preview {
  color: var(--app-color-text-soft);
  line-height: 1.7;
}

.history-page__actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.history-page__preview {
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 0;
}

.history-page__block {
  padding: 16px;
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-color-border);
  background: var(--app-panel-bg-soft);
}

.history-page__block h3 {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.history-page__block p,
.history-page__summary {
  color: var(--app-color-text);
  line-height: 1.8;
}

.history-page__summary :deep(h1) {
  font-size: 20px;
}

@media (max-width: 1100px) {
  .history-page__layout,
  .history-page__filters {
    grid-template-columns: 1fr;
  }
}
</style>
