<template>
  <article class="fragment-card" :class="`status-${fragment.status || 'todo'}`">
    <div class="fragment-card__dot"></div>

    <div class="fragment-card__main">
      <div class="fragment-card__topline">
        <div class="fragment-card__meta">
          <el-tag size="small" :type="statusType" effect="light">{{ statusLabel }}</el-tag>
          <el-tag size="small" effect="plain">{{ fragment.tag || '未分类' }}</el-tag>
          <el-tag size="small" effect="plain">{{ priorityLabel }}</el-tag>
        </div>
        <span class="fragment-card__date">{{ displayDate }}</span>
      </div>

      <h4 class="fragment-card__title">{{ fragment.title || '未命名碎片' }}</h4>
      <p class="fragment-card__text">{{ fragment.content || '暂无详细描述' }}</p>
    </div>

    <div class="fragment-card__actions">
      <el-button size="small" text @click="$emit('edit', fragment)" title="编辑">
        <el-icon><EditPen /></el-icon>
      </el-button>
      <el-button size="small" text :disabled="!canMoveUp" @click="$emit('move-up', fragment)" title="上移">
        <el-icon><Top /></el-icon>
      </el-button>
      <el-button size="small" text :disabled="!canMoveDown" @click="$emit('move-down', fragment)" title="下移">
        <el-icon><Bottom /></el-icon>
      </el-button>
      <el-button size="small" text type="danger" @click="$emit('delete', fragment.id)" title="删除">
        <el-icon><Delete /></el-icon>
      </el-button>
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

const statusType = computed(() => {
  const map = { todo: 'info', doing: 'warning', done: 'success', blocked: 'danger' }
  return map[props.fragment.status] || 'info'
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
  grid-template-columns: 18px minmax(0, 1fr) auto;
  gap: 14px;
  padding: 16px 18px;
  border-radius: var(--app-radius-xl);
  background: #fff;
  border: 1px solid var(--app-color-border);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.fragment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 16px 34px rgba(15, 23, 42, 0.08);
  border-color: rgba(37, 99, 235, 0.18);
}

.fragment-card__dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  margin-top: 6px;
  background: #94a3b8;
  box-shadow: 0 0 0 4px rgba(148, 163, 184, 0.12);
  flex-shrink: 0;
}

.status-done .fragment-card__dot { background: linear-gradient(180deg, #22c55e, #16a34a); box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.12); }
.status-doing .fragment-card__dot { background: linear-gradient(180deg, #f59e0b, #d97706); box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.12); }
.status-blocked .fragment-card__dot { background: linear-gradient(180deg, #ef4444, #dc2626); box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.12); }
.status-todo .fragment-card__dot { background: linear-gradient(180deg, #64748b, #475569); box-shadow: 0 0 0 4px rgba(100, 116, 139, 0.12); }

.fragment-card__main {
  min-width: 0;
}

.fragment-card__topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.fragment-card__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.fragment-card__date {
  font-size: 12px;
  color: var(--app-color-text-muted);
  white-space: nowrap;
}

.fragment-card__title {
  margin-top: 12px;
  font-size: 15px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.fragment-card__text {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.7;
  color: var(--app-color-text-soft);
  white-space: pre-wrap;
}

.fragment-card__actions {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  margin-left: 4px;
  opacity: 0.75;
}

.fragment-card__actions:hover {
  opacity: 1;
}

.fragment-card__actions :deep(.el-button) {
  width: 30px;
  height: 30px;
  padding: 0;
  border-radius: 10px;
}

@media (max-width: 820px) {
  .fragment-card {
    grid-template-columns: 18px minmax(0, 1fr);
  }

  .fragment-card__actions {
    grid-column: 2;
    justify-content: flex-start;
    margin-left: 0;
    padding-top: 8px;
    flex-wrap: wrap;
  }
}
</style>
