<template>
  <div class="daily-list">
    <section v-for="day in weekDays" :key="day.date" class="daily-section app-surface">
      <div class="daily-section__header">
        <div class="daily-section__heading">
          <p class="daily-section__eyebrow">{{ day.label }}</p>
          <h3>{{ day.date }}</h3>
        </div>
        <div class="daily-section__actions">
          <el-input
            v-model="quickInputs[day.date]"
            size="small"
            placeholder="输入一条快速碎片，回车即可保存"
            @keyup.enter="quickAdd(day.date)"
            class="daily-section__quick-input"
          />
          <el-button size="small" type="primary" plain @click="quickAdd(day.date)">
            <el-icon><Plus /></el-icon>
            快速录入
          </el-button>
          <el-button size="small" @click="$emit('add-detail', day.date)">
            <el-icon><EditPen /></el-icon>
            详细录入
          </el-button>
        </div>
      </div>

      <div class="daily-section__body" @dragover.prevent @drop="handleDropToEnd(day.date)">
        <FragmentCard
          v-for="(fragment, index) in grouped[day.date] || []"
          :key="fragment.id"
          class="draggable-fragment"
          draggable="true"
          :fragment="fragment"
          :can-move-up="index > 0"
          :can-move-down="index < (grouped[day.date] || []).length - 1"
          @dragstart="handleDragStart(day.date, fragment.id)"
          @dragover.prevent
          @drop="handleDrop(day.date, index)"
          @edit="$emit('edit-fragment', $event)"
          @delete="$emit('delete-fragment', $event)"
          @move-up="$emit('move-up', $event)"
          @move-down="$emit('move-down', $event)"
        />
        <el-empty v-if="!(grouped[day.date] || []).length" description="当天暂无记录" :image-size="56" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import { Plus, EditPen } from '@element-plus/icons-vue'
import FragmentCard from './FragmentCard.vue'

const props = defineProps({
  fragments: { type: Array, default: () => [] },
  weekStartDate: { type: String, default: '' },
  weekEndDate: { type: String, default: '' },
  statusFilter: { type: String, default: 'all' },
  tagFilter: { type: String, default: 'all' },
  keyword: { type: String, default: '' }
})

const emit = defineEmits(['add-quick', 'add-detail', 'edit-fragment', 'delete-fragment', 'move-up', 'move-down', 'reorder-day'])

const weekDayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const quickInputs = reactive({})
const dragState = reactive({ sourceDate: '', sourceId: null })

const weekDays = computed(() => {
  const start = props.weekStartDate ? parseLocalDate(props.weekStartDate) : getCurrentWeekMonday()
  return Array.from({ length: 7 }).map((_, idx) => {
    const d = new Date(start)
    d.setDate(start.getDate() + idx)
    return { label: weekDayLabels[idx], date: formatLocalDate(d) }
  })
})

const grouped = computed(() => {
  const map = {}
  const keyword = props.keyword.trim().toLowerCase()
  for (const f of props.fragments) {
    if (props.statusFilter !== 'all' && (f.status || 'todo') !== props.statusFilter) continue
    if (props.tagFilter !== 'all' && (f.tag || '未分类') !== props.tagFilter) continue
    if (keyword) {
      const text = `${f.title || ''} ${f.content || ''}`.toLowerCase()
      if (!text.includes(keyword)) continue
    }
    const date = (f.workDate || '').slice(0, 10)
    if (!map[date]) map[date] = []
    map[date].push(f)
  }
  Object.keys(map).forEach((date) => {
    map[date].sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
  })
  return map
})

const quickAdd = (date) => {
  const text = (quickInputs[date] || '').trim()
  if (!text) return
  emit('add-quick', { date, text })
  quickInputs[date] = ''
}

const handleDragStart = (date, id) => {
  dragState.sourceDate = date
  dragState.sourceId = id
}

const handleDrop = (targetDate, targetIndex) => {
  if (!dragState.sourceId || dragState.sourceDate !== targetDate) return
  const list = [...(grouped.value[targetDate] || [])]
  const from = list.findIndex((f) => f.id === dragState.sourceId)
  if (from < 0) return
  list.splice(targetIndex, 0, ...list.splice(from, 1))
  emit('reorder-day', { date: targetDate, orderedIds: list.map((i) => i.id) })
}

const handleDropToEnd = (targetDate) => {
  if (!dragState.sourceId || dragState.sourceDate !== targetDate) return
  const list = [...(grouped.value[targetDate] || [])]
  const from = list.findIndex((f) => f.id === dragState.sourceId)
  if (from < 0) return
  list.push(list.splice(from, 1)[0])
  emit('reorder-day', { date: targetDate, orderedIds: list.map((i) => i.id) })
}

function getCurrentWeekMonday() {
  const now = new Date()
  const day = now.getDay() || 7
  const monday = new Date(now)
  monday.setDate(now.getDate() - day + 1)
  monday.setHours(0, 0, 0, 0)
  return monday
}

function parseLocalDate(dateStr) {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d)
}

function formatLocalDate(date) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  return `${y}-${m}-${d}`
}
</script>

<style scoped>
.daily-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.daily-section {
  border-radius: var(--app-radius-2xl);
  overflow: hidden;
}

.daily-section__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--app-color-border);
  background: var(--app-panel-bg-soft);
}

.daily-section__heading {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.daily-section__eyebrow {
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.daily-section__heading h3 {
  font-size: 16px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.daily-section__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.daily-section__quick-input {
  width: min(360px, 44vw);
}

.daily-section__body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.draggable-fragment {
  cursor: grab;
}

.draggable-fragment:active {
  cursor: grabbing;
}

@media (max-width: 860px) {
  .daily-section__header {
    flex-direction: column;
    align-items: flex-start;
  }

  .daily-section__quick-input {
    width: 100%;
  }
}
</style>
