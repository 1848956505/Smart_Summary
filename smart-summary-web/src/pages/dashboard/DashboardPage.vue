<template>
  <div class="dashboard-page app-page-shell">
    <div class="dashboard-page__scroll scroll-area">
      <section class="dashboard-page__hero app-surface">
        <div class="dashboard-page__hero-body">
          <div class="dashboard-page__hero-copy">
            <p class="dashboard-page__eyebrow">WORKSPACE</p>
            <h2 class="app-title">今天要处理什么？</h2>
            <p class="app-subtitle dashboard-page__description">
              从碎片整理、智能生成到历史回看，在这里快速进入本周工作流。
            </p>
          </div>

          <div class="dashboard-page__quick">
            <AppButton type="primary" @click="go('/app/generate')">开始生成</AppButton>
            <AppButton @click="go('/app/memos')">打开碎片记录本</AppButton>
          </div>
        </div>
      </section>

      <section class="dashboard-page__grid">
        <AppCard v-for="action in actions" :key="action.key" class="dashboard-page__action-card" compact>
          <template #header>
            <div>
              <p class="dashboard-page__card-eyebrow">{{ action.eyebrow }}</p>
              <h3 class="dashboard-page__card-title">{{ action.title }}</h3>
            </div>
            <el-icon class="dashboard-page__card-icon"><component :is="action.icon" /></el-icon>
          </template>
          <p class="dashboard-page__card-desc">{{ action.description }}</p>
          <div class="dashboard-page__card-footer">
            <AppButton type="primary" text @click="go(action.path)">进入</AppButton>
          </div>
        </AppCard>
      </section>

      <section class="dashboard-page__bottom">
        <AppCard class="dashboard-page__recent">
          <template #header>
            <div>
              <p class="dashboard-page__card-eyebrow">RECENT</p>
              <h3 class="dashboard-page__card-title">最近生成记录</h3>
            </div>
          </template>

          <div v-if="records.length" class="dashboard-page__record-list">
            <button
              v-for="item in records.slice(0, 3)"
              :key="item.id"
              class="dashboard-page__record-item"
              type="button"
              @click="go('/app/history')"
            >
              <div class="dashboard-page__record-main">
                <strong>{{ getStyleLabel(item.style) }}</strong>
                <span>{{ truncate(item.summaryText, 80) }}</span>
              </div>
              <span class="dashboard-page__record-time">{{ formatTime(item.createTime) }}</span>
            </button>
          </div>

          <AppEmpty v-else description="暂无最近生成记录">
            <AppButton type="primary" @click="go('/app/generate')">去生成一条</AppButton>
          </AppEmpty>
        </AppCard>

        <AppCard class="dashboard-page__stats" compact>
          <template #header>
            <div>
              <p class="dashboard-page__card-eyebrow">AI STATUS</p>
              <h3 class="dashboard-page__card-title">AI 状态</h3>
            </div>
          </template>

          <div class="dashboard-page__status-list">
            <div class="dashboard-page__status-row">
              <span>当前模型</span>
              <strong>{{ aiStatus.model }}</strong>
            </div>
            <div class="dashboard-page__status-row">
              <span>响应状态</span>
              <strong>{{ aiStatus.health }}</strong>
            </div>
            <div class="dashboard-page__status-row">
              <span>当前耗时</span>
              <strong>{{ aiStatus.latency }}</strong>
            </div>
          </div>
        </AppCard>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick, Notebook, Clock, Setting } from '@element-plus/icons-vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppEmpty from '@/components/ui/AppEmpty.vue'
import { getStyleLabel } from '@/components/common/themeConfig'
import { settingsService } from '@/services/settings.service'
import { summaryService } from '@/services/summary.service'

const router = useRouter()
const records = ref([])
const modelId = ref('未配置')
const aiHealth = ref('待检测')
const aiLatency = ref('待检测')

const actions = [
  {
    key: 'generate',
    eyebrow: 'SUMMARY',
    title: '智能生成',
    description: '输入工作记录，一键生成结构化总结。',
    icon: MagicStick,
    path: '/app/generate'
  },
  {
    key: 'memos',
    eyebrow: 'MEMOS',
    title: '碎片记录本',
    description: '整理文件夹、周记录与每日碎片。',
    icon: Notebook,
    path: '/app/memos'
  },
  {
    key: 'history',
    eyebrow: 'HISTORY',
    title: '历史周报',
    description: '查看、复制并导出历史生成内容。',
    icon: Clock,
    path: '/app/history'
  },
  {
    key: 'settings',
    eyebrow: 'SETTINGS',
    title: '系统设置',
    description: '统一管理个人信息与模型参数。',
    icon: Setting,
    path: '/app/settings'
  }
]

const aiStatus = computed(() => ({
  model: modelId.value || '未配置',
  health: aiHealth.value,
  latency: aiLatency.value
}))

const go = (path) => {
  router.push(path)
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
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

const loadRecords = async () => {
  try {
    const { data } = await summaryService.listHistory()
    records.value = data.success ? data.data || [] : []
  } catch {
    records.value = []
  }
}

const loadSettingsAndHealth = async () => {
  try {
    const { data } = await settingsService.get()
    const config = data?.success ? data.data || {} : {}
    modelId.value = config.modelId || '未配置'

    if (config.baseUrl && config.apiKey && config.modelId) {
      const testResponse = await settingsService.testConnection({
        baseUrl: config.baseUrl,
        apiKey: config.apiKey,
        modelId: config.modelId
      })
      const result = testResponse.data || {}
      aiHealth.value = result.success ? '正常' : '异常'
      aiLatency.value = typeof result.latencyMs === 'number'
        ? `${(result.latencyMs / 1000).toFixed(1)}s`
        : '暂无数据'
    } else {
      aiHealth.value = '待配置'
      aiLatency.value = '暂无数据'
    }
  } catch {
    aiHealth.value = '异常'
    aiLatency.value = '暂无数据'
  }
}

onMounted(async () => {
  await Promise.all([loadRecords(), loadSettingsAndHealth()])
})
</script>

<style scoped>
.dashboard-page {
  gap: var(--app-space-5);
  flex: 1;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  min-width: 0;
  overflow: hidden;
}

.dashboard-page__scroll {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-5);
  flex: 1 1 0;
  min-height: 0;
  height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding: var(--app-space-4);
  padding-right: calc(var(--app-space-4) + 4px);
}

.dashboard-page__scroll > * {
  flex: 0 0 auto;
  width: 100%;
}

.dashboard-page__hero {
  border-radius: var(--app-radius-2xl);
  border: 1px solid var(--memo-border);
  background: rgba(255, 255, 255, 0.84);
  box-shadow: 0 14px 34px rgba(39, 72, 124, 0.06);
}

.dashboard-page__hero-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
}

.dashboard-page__hero-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.dashboard-page__hero-copy .app-title {
  font-size: 18px;
  line-height: 1.25;
}

.dashboard-page__eyebrow,
.dashboard-page__card-eyebrow {
  margin: 0;
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--app-color-text-muted);
}

.dashboard-page__description {
  margin: 0;
  max-width: 560px;
  font-size: 13px;
  line-height: 1.45;
}

.dashboard-page__quick {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  margin-left: auto;
  flex-shrink: 0;
}

.dashboard-page__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--app-space-4);
}

.dashboard-page__action-card {
  min-height: 188px;
}

.dashboard-page__card-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.dashboard-page__card-icon {
  font-size: 24px;
  color: var(--app-color-primary);
}

.dashboard-page__card-desc {
  margin: 12px 0 14px;
  color: var(--app-color-text-soft);
  line-height: 1.7;
}

.dashboard-page__card-footer,
.dashboard-page__record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.dashboard-page__bottom {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: var(--app-space-4);
}

.dashboard-page__record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dashboard-page__record-item {
  width: 100%;
  border: 0;
  background: transparent;
  border-radius: var(--app-radius-lg);
  padding: 10px 0;
  cursor: pointer;
  text-align: left;
  border-bottom: 1px solid var(--app-border-default);
}

.dashboard-page__record-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.dashboard-page__record-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
}

.dashboard-page__record-main strong {
  font-size: 14px;
  color: var(--app-color-primary);
}

.dashboard-page__record-main span {
  color: var(--app-color-text-soft);
  line-height: 1.55;
}

.dashboard-page__record-time {
  flex-shrink: 0;
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.dashboard-page__status-list {
  display: grid;
  gap: 16px;
  margin-top: 4px;
}

.dashboard-page__status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 2px 14px;
  border-bottom: 1px solid var(--app-border-default);
}

.dashboard-page__status-row:last-child {
  padding-bottom: 0;
  border-bottom: 0;
}

.dashboard-page__status-row span {
  color: var(--app-color-text-muted);
}

.dashboard-page__status-row strong {
  font-size: 16px;
  color: var(--app-color-text-strong);
  text-align: right;
}

@media (max-width: 1280px) {
  .dashboard-page__grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-page__bottom {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .dashboard-page__hero-body {
    flex-direction: column;
    align-items: flex-start;
  }

  .dashboard-page__quick {
    margin-left: 0;
    justify-content: flex-start;
  }

  .dashboard-page__grid {
    grid-template-columns: 1fr;
  }
}
</style>

