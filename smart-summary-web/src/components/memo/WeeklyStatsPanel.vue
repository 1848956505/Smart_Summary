<template>
  <section class="stats-panel app-surface">
    <div class="stats-panel__header">
      <div>
        <p class="stats-panel__eyebrow">概览</p>
        <h3>本周统计</h3>
      </div>
      <span class="memo-chip memo-chip--accent stats-panel__chip">{{ totalCount }} 条碎片</span>
    </div>

    <div class="stats-panel__section">
      <p class="stats-panel__label">状态分布</p>
      <div v-for="item in statusRows" :key="item.key" class="stats-panel__row">
        <span class="stats-panel__name">{{ item.label }}</span>
        <div class="stats-panel__bar">
          <div class="stats-panel__fill" :style="{ width: item.percent + '%', background: item.color }"></div>
        </div>
        <span class="stats-panel__value">{{ item.value }}</span>
      </div>
    </div>

    <div class="stats-panel__section" v-if="tagRows.length">
      <p class="stats-panel__label">标签分布</p>
      <div class="stats-panel__tags">
        <div v-for="item in tagRows" :key="item.key" class="stats-panel__tag">
          <span class="memo-chip memo-chip--content">{{ item.label }}</span>
          <b>{{ item.value }}</b>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({ fragments: { type: Array, default: () => [] } })

const totalCount = computed(() => props.fragments.length)
const total = computed(() => props.fragments.length || 1)

const statusRows = computed(() => {
  const map = { todo: 0, doing: 0, done: 0, blocked: 0 }
  for (const f of props.fragments) {
    const key = f.status || 'todo'
    if (map[key] !== undefined) map[key] += 1
  }
  const meta = {
    todo: { label: '待办', color: '#64748b' },
    doing: { label: '进行中', color: '#f59e0b' },
    done: { label: '已完成', color: '#22c55e' },
    blocked: { label: '阻塞', color: '#ef4444' }
  }
  return Object.keys(map).map((key) => ({
    key,
    label: meta[key].label,
    value: map[key],
    color: meta[key].color,
    percent: Math.round((map[key] / total.value) * 100)
  }))
})

const tagRows = computed(() => {
  const counter = {}
  for (const f of props.fragments) {
    const tag = f.tag || '未分类'
    counter[tag] = (counter[tag] || 0) + 1
  }
  return Object.entries(counter)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 6)
    .map(([key, value]) => ({ key, label: key, value }))
})
</script>

<style scoped>
.stats-panel {
  padding: 18px;
  border-radius: var(--app-radius-2xl);
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.stats-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.stats-panel__eyebrow {
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.stats-panel h3 {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.stats-panel__section {
  margin-top: 18px;
}

.stats-panel__section:last-child {
  margin-bottom: 0;
}

.stats-panel__label {
  margin-bottom: 10px;
  font-size: 13px;
  font-weight: 700;
  color: var(--app-color-text-soft);
}

.stats-panel__row {
  display: grid;
  grid-template-columns: 58px 1fr 28px;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.stats-panel__name,
.stats-panel__value {
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.stats-panel__value {
  text-align: right;
}

.stats-panel__bar {
  height: 10px;
  background: color-mix(in srgb, var(--app-surface-soft) 84%, transparent);
  border-radius: 999px;
  overflow: hidden;
}

.stats-panel__fill {
  height: 100%;
  border-radius: inherit;
}

.stats-panel__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-content: flex-start;
}

.stats-panel__tag {
  min-width: 92px;
  padding: 10px 12px;
  border-radius: 16px;
  background: var(--app-surface-elevated-max);
  border: 1px solid var(--app-color-border);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
}

.stats-panel__tag b {
  font-size: 14px;
  color: var(--app-color-text-strong);
}
</style>
