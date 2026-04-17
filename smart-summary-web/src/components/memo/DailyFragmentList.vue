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
          class="daily-section__calendar"
          :class="{ 'daily-section__calendar--active': activeDate === day.date }"
          @click="$emit('select-date', day.date)"
          :title="`选中 ${day.date}`"
        >
          <span class="daily-section__calendar-prefix">{{ day.prefix }}</span>
          <span class="daily-section__calendar-day">{{ day.day }}</span>
        </button>

        <div class="daily-section__heading">
          <div class="daily-section__title-row">
            <h3>{{ day.date }}</h3>
            <span v-if="activeDate === day.date" class="daily-section__active-chip">Active</span>
          </div>
          <p class="daily-section__eyebrow">{{ day.label }}</p>
        </div>

        <div class="daily-section__summary">
          <span class="daily-section__count">{{ (grouped[day.date] || []).length }} 条</span>
          <span class="daily-section__hint">点击日历块可切换录入日期</span>
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
        <el-empty v-if="!(grouped[day.date] || []).length" description="当天暂无记录" :image-size="56" />
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
const weekDayPrefixes = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
const dragState = reactive({ sourceDate: '', sourceId: null })

const weekDays = computed(() => {
  const start = props.weekStartDate ? parseLocalDate(props.weekStartDate) : getCurrentWeekMonday()
  return Array.from({ length: 7 }).map((_, idx) => {
    const d = new Date(start)
    d.setDate(start.getDate() + idx)
    return {
      label: weekDayLabels[idx],
      prefix: weekDayPrefixes[idx],
      date: formatLocalDate(d),
      day: String(d.getDate()).padStart(2, '0')
    }
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
  gap: 18px;
  position: relative;
}

.daily-list::before {
  content: '';
  position: absolute;
  left: 42px;
  top: 10px;
  bottom: 10px;
  width: 1px;
  background: linear-gradient(to bottom, transparent, rgba(148, 163, 184, 0.45) 10%, rgba(148, 163, 184, 0.45) 90%, transparent);
}

.daily-section {
  position: relative;
  padding: 4px 0 0;
}

.daily-section--active .daily-section__heading h3 {
  color: var(--app-color-primary-strong);
}

.daily-section__header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 14px;
}

.daily-section__calendar {
  width: 52px;
  height: 60px;
  padding: 8px 0 6px;
  border-radius: 18px;
  border: 1px solid var(--app-color-border);
  background: #fff;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
}

.daily-section__calendar--active {
  border-color: rgba(37, 99, 235, 0.26);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.12);
  transform: translateY(-1px);
}

.daily-section__calendar-prefix {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
  color: var(--app-color-primary);
  line-height: 1;
  margin-bottom: 4px;
}

.daily-section__calendar-day {
  font-size: 21px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  line-height: 1;
}

.daily-section__heading {
  min-width: 0;
  flex: 1;
}

.daily-section__title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.daily-section__heading h3 {
  font-size: 17px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.daily-section__active-chip {
  padding: 4px 8px;
  border-radius: 999px;
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.daily-section__eyebrow {
  margin-top: 5px;
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.daily-section__summary {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-end;
  text-align: right;
  min-width: 0;
}

.daily-section__count {
  font-size: 12px;
  font-weight: 700;
  color: var(--app-color-text-strong);
}

.daily-section__hint {
  font-size: 11px;
  color: var(--app-color-text-muted);
}

.daily-section__body {
  position: relative;
  margin-left: 68px;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.daily-section__body::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 1px;
  background: rgba(226, 232, 240, 0.85);
}

.daily-section__item {
  position: relative;
}

.daily-section__rail-dot {
  position: absolute;
  left: -24px;
  top: 22px;
  width: 13px;
  height: 13px;
  border-radius: 50%;
  background: #94a3b8;
  border: 3px solid #fff;
  box-shadow: 0 0 0 1px rgba(148, 163, 184, 0.15);
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
    align-items: flex-start;
    flex-direction: column;
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
