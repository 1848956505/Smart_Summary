<template>
  <div class="dashboard-page app-page-shell">
    <section class="dashboard-page__hero app-card">
      <div class="app-card__body dashboard-page__hero-body">
        <div>
          <p class="dashboard-page__eyebrow">WORKSPACE</p>
          <h2 class="app-title">今天要处理什么？</h2>
          <p class="app-subtitle dashboard-page__description">
            这里集中放置生成、碎片、历史与设置入口，保持稳定、克制、清晰的协作工作台体验。
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
          <span>{{ action.meta }}</span>
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
          <button v-for="item in records.slice(0, 3)" :key="item.id" class="dashboard-page__record-item" @click="go('/app/history')">
            <div class="dashboard-page__record-main">
              <strong>{{ item.style || 'dingtalk' }}</strong>
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
            <p class="dashboard-page__card-eyebrow">STATUS</p>
            <h3 class="dashboard-page__card-title">系统状态</h3>
          </div>
        </template>
        <div class="dashboard-page__status-list">
          <div class="dashboard-page__status-item">
            <span>当前主题</span>
            <strong>浅色企业工作台</strong>
          </div>
          <div class="dashboard-page__status-item">
            <span>工作模式</span>
            <strong>智能总结 / 碎片整理</strong>
          </div>
          <div class="dashboard-page__status-item">
            <span>登录状态</span>
            <strong>已认证</strong>
          </div>
        </div>
      </AppCard>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { MagicStick, Notebook, Clock, Setting } from '@element-plus/icons-vue'
import AppButton from '@/components/ui/AppButton.vue'
import AppCard from '@/components/ui/AppCard.vue'
import AppEmpty from '@/components/ui/AppEmpty.vue'
import { summaryService } from '@/services/summary.service'

const router = useRouter()
const records = ref([])

const actions = computed(() => [
  { key: 'generate', eyebrow: 'SUMMARY', title: '智能生成', description: '输入工作记录，一键生成结构化总结。', meta: '快速输出周报 / 月报', icon: MagicStick, path: '/app/generate' },
  { key: 'memos', eyebrow: 'MEMOS', title: '碎片记录本', description: '整理文件夹、周记录与每日碎片。', meta: '三栏工作台 / 归档追溯', icon: Notebook, path: '/app/memos' },
  { key: 'history', eyebrow: 'HISTORY', title: '历史周报', description: '查看、复制并导出历史生成内容。', meta: '可追溯 / 可复用', icon: Clock, path: '/app/history' },
  { key: 'settings', eyebrow: 'SETTINGS', title: '系统设置', description: '统一管理个人信息与模型参数。', meta: '基础信息 / 模型配置', icon: Setting, path: '/app/settings' }
])

const loadRecords = async () => {
  try {
    const { data } = await summaryService.listHistory()
    if (data.success) records.value = data.data || []
  } catch {
    records.value = []
  }
}

const go = (path) => {
  router.push(path)
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const truncate = (text, limit) => {
  const value = text || ''
  return value.length > limit ? `${value.slice(0, limit)}...` : value
}

onMounted(loadRecords)
</script>

<style scoped>
.dashboard-page {
  gap: var(--app-space-5);
}

.dashboard-page__hero-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--app-space-5);
}

.dashboard-page__eyebrow,
.dashboard-page__card-eyebrow {
  margin: 0 0 6px;
  font-size: 12px;
  letter-spacing: 0.16em;
  color: var(--app-color-text-muted);
}

.dashboard-page__description {
  max-width: 780px;
  margin-top: 10px;
}

.dashboard-page__quick {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.dashboard-page__grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--app-space-4);
}

.dashboard-page__action-card {
  min-height: 220px;
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
  margin: 14px 0 18px;
  color: var(--app-color-text-soft);
  line-height: 1.7;
}

.dashboard-page__card-footer,
.dashboard-page__status-item,
.dashboard-page__record-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--app-space-3);
}

.dashboard-page__record-item {
  width: 100%;
  text-align: left;
  padding: 14px 0;
  border-top: 1px solid var(--app-panel-border);
}

.dashboard-page__record-item:first-child {
  border-top: 0;
  padding-top: 0;
}

.dashboard-page__record-main {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.dashboard-page__record-main strong {
  font-size: 13px;
  color: var(--app-color-text-strong);
}

.dashboard-page__record-main span,
.dashboard-page__record-time,
.dashboard-page__status-item span {
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.dashboard-page__status-list {
  display: grid;
  gap: 12px;
}

.dashboard-page__status-item {
  padding: 14px;
  border-radius: var(--app-radius-lg);
  background: var(--app-panel-bg-soft);
  border: 1px solid var(--app-panel-border);
}

.dashboard-page__bottom {
  display: grid;
  grid-template-columns: 1.3fr 0.7fr;
  gap: var(--app-space-4);
}

@media (max-width: 1280px) {
  .dashboard-page__grid,
  .dashboard-page__bottom {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .dashboard-page__hero-body,
  .dashboard-page__grid,
  .dashboard-page__bottom {
    grid-template-columns: 1fr;
    display: grid;
  }
}
</style>
