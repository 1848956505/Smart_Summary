<template>
  <article class="fragment-card" :class="`status-${fragment.status || 'todo'}`">
    <div class="fragment-card__main">
      <div class="fragment-card__topline">
        <div class="fragment-card__meta">
          <span :class="['memo-chip', 'memo-chip--state', statusChipClass]">{{ statusLabel }}</span>
          <span class="memo-chip memo-chip--content">{{ fragment.tag || '未分类' }}</span>
          <span class="memo-chip memo-chip--soft">{{ priorityLabel }}</span>
        </div>
        <span class="fragment-card__date">{{ displayDate }}</span>
      </div>

      <h4 class="fragment-card__title">{{ fragment.title || '未命名碎片' }}</h4>
      <p class="fragment-card__text">{{ fragment.content || '暂无详细描述' }}</p>
    </div>

    <div class="fragment-card__actions">
      <button class="memo-button memo-button--ghost memo-button--icon" type="button" title="编辑" @click="$emit('edit', fragment)">
        <el-icon><EditPen /></el-icon>
      </button>
      <button class="memo-button memo-button--ghost memo-button--icon" type="button" title="上移" :disabled="!canMoveUp" @click="$emit('move-up', fragment)">
        <el-icon><Top /></el-icon>
      </button>
      <button class="memo-button memo-button--ghost memo-button--icon" type="button" title="下移" :disabled="!canMoveDown" @click="$emit('move-down', fragment)">
        <el-icon><Bottom /></el-icon>
      </button>
      <button class="memo-button memo-button--ghost memo-button--icon fragment-card__danger" type="button" title="删除" @click="$emit('delete', fragment.id)">
        <el-icon><Delete /></el-icon>
      </button>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { EditPen, Top, Bottom, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  fragment: { type: Object, required: true },
  canMoveUp: { type: Boolean, default: false },
  canMoveDown: { type: Boolean, default: false }
})

defineEmits(['edit', 'delete', 'move-up', 'move-down'])

const statusLabel = computed(() => {
  const map = { todo: '待办', doing: '进行中', done: '已完成', blocked: '阻塞' }
  return map[props.fragment.status] || '待办'
})

const statusChipClass = computed(() => {
  const map = { todo: 'memo-chip--info', doing: 'memo-chip--warning', done: 'memo-chip--success', blocked: 'memo-chip--danger' }
  return map[props.fragment.status] || 'memo-chip--info'
})

const priorityLabel = computed(() => {
  const map = { low: '低优先级', medium: '中优先级', high: '高优先级' }
  return map[props.fragment.priority] || '中优先级'
})

const displayDate = computed(() => (props.fragment.workDate || '').slice(0, 10))
</script>

<style scoped>
.fragment-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  padding: 18px 20px;
  border-radius: 22px;
  background: var(--memo-surface-strong);
  border: 1px solid var(--memo-border);
  box-shadow: var(--memo-shadow-soft);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.fragment-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--memo-shadow-strong);
  border-color: var(--memo-border-strong);
}

.fragment-card__main {
  min-width: 0;
}

.fragment-card__topline {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.fragment-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.fragment-card__date {
  font-size: 11px;
  color: var(--app-color-text-muted);
  white-space: nowrap;
  letter-spacing: 0.02em;
  padding-top: 4px;
}

.fragment-card__title {
  margin-top: 14px;
  font-size: 16px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  line-height: 1.45;
}

.fragment-card__text {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.8;
  color: var(--app-color-text-soft);
  white-space: pre-wrap;
}

.fragment-card__actions {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-left: 4px;
  opacity: 0.44;
  transition: opacity 0.2s ease;
}

.fragment-card:hover .fragment-card__actions,
.fragment-card:focus-within .fragment-card__actions {
  opacity: 1;
}

.fragment-card__danger {
  color: var(--app-color-danger);
}

.fragment-card__danger:hover {
  color: var(--app-color-danger);
  border-color: rgba(209, 67, 67, 0.18);
  background: rgba(255, 244, 244, 0.98);
}

@media (max-width: 820px) {
  .fragment-card {
    grid-template-columns: minmax(0, 1fr);
  }

  .fragment-card__topline {
    flex-direction: column;
    align-items: flex-start;
  }

  .fragment-card__actions {
    grid-column: 1;
    justify-content: flex-start;
    margin-left: 0;
    padding-top: 8px;
    flex-wrap: wrap;
    opacity: 1;
  }
}
</style>
