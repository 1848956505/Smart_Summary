<template>
  <section class="week-header app-surface">
    <div class="week-header__identity">
      <div class="week-header__eyebrow-row">
        <p class="week-header__eyebrow">周记录上下文</p>
        <span class="memo-chip memo-chip--state memo-chip--info week-header__status-chip">
          {{ currentWeek ? '已激活' : '未选择周记录' }}
        </span>
      </div>

      <h2>{{ currentWeek?.title || '请选择一个周记录' }}</h2>
      <p v-if="currentWeek" class="week-header__range">{{ currentWeek.weekStartDate }} - {{ currentWeek.weekEndDate }}</p>
    </div>

    <div v-if="currentWeek" class="week-header__meta">
      <span class="week-header__meta-item"><b>{{ stats.total || 0 }}</b><small>碎片</small></span>
      <span class="week-header__meta-item"><b>{{ stats.done || 0 }}</b><small>已完成</small></span>
      <span class="week-header__meta-item"><b>{{ stats.doing || 0 }}</b><small>进行中</small></span>
      <span class="week-header__meta-item"><b>{{ stats.blocked || 0 }}</b><small>阻塞</small></span>
    </div>

    <div v-if="currentWeek" class="week-header__actions">
      <el-button size="small" class="memo-button memo-button--ghost week-header__ghost" @click="$emit('open-stats')">
        <el-icon><Grid /></el-icon>
        统计
      </el-button>
      <el-button size="small" class="memo-button memo-button--primary week-header__primary" :loading="generating" @click="$emit('generate')">
        <el-icon><MagicStick /></el-icon>
        一键生成周报
      </el-button>
      <el-dropdown trigger="click">
        <el-button size="small" class="memo-button memo-button--ghost week-header__more">
          <el-icon><MoreFilled /></el-icon>
          更多
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="$emit('save')"><el-icon><FolderOpened /></el-icon>保存到历史</el-dropdown-item>
            <el-dropdown-item @click="$emit('copy')"><el-icon><CopyDocument /></el-icon>复制周报</el-dropdown-item>
            <el-dropdown-item @click="$emit('export-markdown')"><el-icon><Document /></el-icon>导出文本</el-dropdown-item>
            <el-dropdown-item @click="$emit('export-pdf')"><el-icon><Printer /></el-icon>导出打印件</el-dropdown-item>
            <el-dropdown-item @click="$emit('archive')"><el-icon><Finished /></el-icon>归档</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </section>
</template>

<script setup>
import { MagicStick, FolderOpened, CopyDocument, Document, Printer, Finished, Grid, MoreFilled } from '@element-plus/icons-vue'

defineProps({
  currentWeek: { type: Object, default: null },
  stats: { type: Object, default: () => ({}) },
  generating: { type: Boolean, default: false }
})

defineEmits(['generate', 'save', 'copy', 'export-markdown', 'export-pdf', 'archive', 'open-stats'])
</script>

<style scoped>
.week-header {
  padding: 12px 16px;
  border-radius: var(--app-radius-2xl);
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) auto auto;
  gap: 12px;
  align-items: center;
  background: var(--memo-surface-strong);
  border: 1px solid var(--memo-border);
}

.week-header__identity {
  min-width: 0;
}

.week-header__eyebrow-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.week-header__eyebrow {
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.week-header__status-chip {
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.week-header__identity h2 {
  margin-top: 8px;
  font-size: 18px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  line-height: 1.2;
}

.week-header__range {
  margin-top: 8px;
  font-size: 11px;
  color: var(--app-color-text-soft);
}

.week-header__meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.week-header__meta-item {
  min-width: 64px;
  padding: 7px 9px;
  border-radius: 12px;
  background: var(--memo-surface-muted);
  border: 1px solid var(--memo-border);
  display: flex;
  flex-direction: column;
  gap: 4px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.week-header__meta-item:hover {
  border-color: var(--memo-border-strong);
  box-shadow: 0 8px 18px rgba(39, 72, 124, 0.06);
}

.week-header__meta-item b {
  font-size: 14px;
  color: var(--app-color-text-strong);
  line-height: 1;
}

.week-header__meta-item small {
  font-size: 10px;
  color: var(--app-color-text-muted);
}

.week-header__actions {
  display: flex;
  align-items: center;
  gap: 6px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.week-header__primary {
  min-width: 116px;
}

@media (max-width: 1280px) {
  .week-header {
    grid-template-columns: minmax(0, 1fr);
  }

  .week-header__actions {
    justify-content: flex-start;
  }
}

@media (max-width: 860px) {
  .week-header {
    padding: 14px 16px;
  }

  .week-header__meta-item {
    min-width: calc(50% - 4px);
  }
}
</style>
