<template>
  <div class="daily-list">
    <section
      v-for="day in weekDays"
      :key="day.date"
      :id="`memo-day-${day.date}`"
      class="daily-section"
      :class="{ 'daily-section--active': activeDate === day.date }"
    >
      <div class="daily-section__header">
        <button
          class="daily-section__anchor"
          :class="{ 'daily-section__anchor--active': activeDate === day.date }"
          :title="`选中 ${day.date}`"
          @click="$emit('select-date', day.date)"
        >
          <span class="daily-section__anchor-prefix">{{ day.prefix }}</span>
          <span class="daily-section__anchor-day">{{ day.day }}</span>
        </button>

        <div class="daily-section__heading">
          <div class="daily-section__title-row">
            <h3>{{ day.date }}</h3>
            <span v-if="activeDate === day.date" class="memo-chip memo-chip--accent daily-section__active-chip">当前</span>
          </div>
          <p class="daily-section__eyebrow">{{ day.label }}</p>
        </div>

        <div class="daily-section__summary">
          <span class="daily-section__count">{{ (grouped[day.date] || []).length }} 条</span>
          <span class="daily-section__hint">点击日期锚点可切换录入日期</span>
        </div>
      </div>

      <div class="daily-section__body" @dragover.prevent @drop="handleDropToEnd(day.date)">
        <div
          v-for="(fragment, index) in grouped[day.date] || []"
          :key="fragment.id"
          class="daily-section__item"
        >
          <div class="daily-section__rail-dot"></div>
          <FragmentCard
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
        </div>

        <el-empty v-if="!(grouped[day.date] || []).length" description="当日暂无记录" :image-size="56" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive } from 'vue'
import FragmentCard from './FragmentCard.vue'

const props = defineProps({
  fragments: { type: Array, default: () => [] },
  weekStartDate: { type: String, default: '' },
  weekEndDate: { type: String, default: '' },
  activeDate: { type: String, default: '' },
  statusFilter: { type: String, default: 'all' },
  tagFilter: { type: String, default: 'all' },
  keyword: { type: String, default: '' }
})

const emit = defineEmits(['edit-fragment', 'delete-fragment', 'move-up', 'move-down', 'reorder-day', 'select-date'])

const weekDayLabels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const dragState = reactive({ sourceDate: '', sourceId: null })

const weekDays = computed(() => {
  const start = props.weekStartDate ? parseLocalDate(props.weekStartDate) : getCurrentWeekMonday()
  return Array.from({ length: 7 }).map((_, idx) => {
    const date = new Date(start)
    date.setDate(start.getDate() + idx)
    return {
      label: weekDayLabels[idx],
      prefix: weekDayLabels[idx],
      date: formatLocalDate(date),
      day: String(date.getDate()).padStart(2, '0')
    }
  })
})

const grouped = computed(() => {
  const map = {}
  const keyword = props.keyword.trim().toLowerCase()

  for (const fragment of props.fragments) {
    if (props.statusFilter !== 'all' && (fragment.status || 'todo') !== props.statusFilter) continue
    if (props.tagFilter !== 'all' && (fragment.tag || '未分类') !== props.tagFilter) continue

    if (keyword) {
      const text = `${fragment.title || ''} ${fragment.content || ''}`.toLowerCase()
      if (!text.includes(keyword)) continue
    }

    const date = (fragment.workDate || '').slice(0, 10)
    if (!map[date]) map[date] = []
    map[date].push(fragment)
  }

  Object.keys(map).forEach((date) => {
    map[date].sort((a, b) => (a.sortOrder || 0) - (b.sortOrder || 0))
  })

  return map
})

const handleDragStart = (date, id) => {
  dragState.sourceDate = date
  dragState.sourceId = id
}

const handleDrop = (targetDate, targetIndex) => {
  if (!dragState.sourceId || dragState.sourceDate !== targetDate) return
  const list = [...(grouped.value[targetDate] || [])]
  const from = list.findIndex((fragment) => fragment.id === dragState.sourceId)
  if (from < 0) return
  list.splice(targetIndex, 0, ...list.splice(from, 1))
  emit('reorder-day', { date: targetDate, orderedIds: list.map((item) => item.id) })
}

const handleDropToEnd = (targetDate) => {
  if (!dragState.sourceId || dragState.sourceDate !== targetDate) return
  const list = [...(grouped.value[targetDate] || [])]
  const from = list.findIndex((fragment) => fragment.id === dragState.sourceId)
  if (from < 0) return
  list.push(list.splice(from, 1)[0])
  emit('reorder-day', { date: targetDate, orderedIds: list.map((item) => item.id) })
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
  const [year, month, day] = dateStr.split('-').map(Number)
  return new Date(year, month - 1, day)
}

function formatLocalDate(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}
</script>

<style scoped>
.daily-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
  position: relative;
}

.daily-list::before {
  content: '';
  position: absolute;
  left: 32px;
  top: 12px;
  bottom: 12px;
  width: 1px;
  background: linear-gradient(to bottom, transparent, var(--memo-line) 12%, var(--memo-line) 88%, transparent);
}

.daily-section {
  position: relative;
  padding: 6px 0 14px;
}

.daily-section--active .daily-section__heading h3 {
  color: var(--app-color-primary-strong);
}

.daily-section__header {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.daily-section__anchor {
  width: 42px;
  height: 52px;
  padding: 6px 0 5px;
  border-radius: 16px;
  border: 1px solid var(--memo-border);
  background: var(--memo-surface-strong);
  box-shadow: var(--memo-shadow-soft);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 1;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.daily-section__anchor--active {
  border-color: var(--memo-border-strong);
  box-shadow: var(--memo-selected-shadow);
  transform: translateY(-1px);
}

.daily-section__anchor-prefix {
  font-size: 8px;
  font-weight: 800;
  letter-spacing: 0.14em;
  color: var(--app-color-primary-strong);
  line-height: 1;
  margin-bottom: 5px;
}

.daily-section__anchor-day {
  font-size: 16px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  line-height: 1;
}

.daily-section__heading {
  min-width: 0;
}

.daily-section__title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.daily-section__heading h3 {
  font-size: 15px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.daily-section__active-chip {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.45);
}

.daily-section__eyebrow {
  margin-top: 5px;
  color: var(--app-color-text-muted);
  font-size: 11px;
}

.daily-section__summary {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-end;
  text-align: right;
}

.daily-section__count {
  font-size: 11px;
  font-weight: 700;
  color: var(--app-color-text-strong);
}

.daily-section__hint {
  font-size: 10px;
  color: var(--app-color-text-muted);
}

.daily-section__body {
  position: relative;
  margin-left: 52px;
  padding-left: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.daily-section__body::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 1px;
  background: var(--memo-line-soft);
}

.daily-section__item {
  position: relative;
}

.daily-section__rail-dot {
  position: absolute;
  left: -21px;
  top: 16px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--app-color-primary);
  border: 3px solid var(--memo-surface-strong);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.14);
  z-index: 1;
}

.draggable-fragment {
  cursor: grab;
}

.draggable-fragment:active {
  cursor: grabbing;
}

@media (max-width: 860px) {
  .daily-section__header {
    grid-template-columns: minmax(0, 1fr);
    align-items: flex-start;
  }

  .daily-section__summary {
    align-items: flex-start;
    text-align: left;
  }

  .daily-list::before,
  .daily-section__body::before {
    display: none;
  }

  .daily-section__body {
    margin-left: 0;
    padding-left: 0;
  }

  .daily-section__rail-dot {
    display: none;
  }
}
</style>
