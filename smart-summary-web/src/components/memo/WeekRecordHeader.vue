<template>
  <section class="week-header app-surface">
    <div class="week-header__info">
      <div class="week-header__eyebrow-row">
        <p class="week-header__eyebrow">Week Workspace</p>
        <el-tag size="small" effect="plain">{{ currentWeek ? 'Active' : 'No Week Selected' }}</el-tag>
      </div>
      <h2>{{ currentWeek?.title || '请选择一个周记录' }}</h2>
      <div v-if="currentWeek" class="week-header__meta">
        <span>周期：{{ currentWeek.weekStartDate }} ~ {{ currentWeek.weekEndDate }}</span>
        <span>碎片：{{ stats.total || 0 }}</span>
        <span>已完成：{{ stats.done || 0 }}</span>
        <span>进行中：{{ stats.doing || 0 }}</span>
        <span>阻塞：{{ stats.blocked || 0 }}</span>
      </div>
    </div>
    <div class="week-header__actions" v-if="currentWeek">
      <el-button size="small" type="primary" :loading="generating" @click="$emit('generate')">
        <el-icon><MagicStick /></el-icon>
        一键生成周报
      </el-button>
      <el-button size="small" @click="$emit('save')">
        <el-icon><FolderOpened /></el-icon>
        保存到历史
      </el-button>
      <el-button size="small" @click="$emit('copy')">
        <el-icon><CopyDocument /></el-icon>
        复制周报
      </el-button>
      <el-button size="small" @click="$emit('export-markdown')">
        <el-icon><Document /></el-icon>
        导出 Markdown
      </el-button>
      <el-button size="small" @click="$emit('export-pdf')">
        <el-icon><Printer /></el-icon>
        导出 PDF
      </el-button>
      <el-button size="small" type="warning" plain @click="$emit('archive')">
        <el-icon><Finished /></el-icon>
        归档
      </el-button>
    </div>
  </section>
</template>

<script setup>
import { MagicStick, FolderOpened, CopyDocument, Document, Printer, Finished } from '@element-plus/icons-vue'

defineProps({
  currentWeek: { type: Object, default: null },
  stats: { type: Object, default: () => ({}) },
  generating: { type: Boolean, default: false }
})

defineEmits(['generate', 'save', 'copy', 'export-markdown', 'export-pdf', 'archive'])
</script>

<style scoped>
.week-header {
  padding: 20px 22px;
  border-radius: var(--app-radius-2xl);
  display: flex;
  justify-content: space-between;
  gap: 18px;
}

.week-header__info {
  min-width: 0;
}

.week-header__eyebrow-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.week-header__eyebrow {
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.week-header__info h2 {
  margin-top: 10px;
  font-size: 22px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.week-header__meta {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  font-size: 13px;
  color: var(--app-color-text-soft);
  flex-wrap: wrap;
}

.week-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 1100px) {
  .week-header {
    flex-direction: column;
  }

  .week-header__actions {
    justify-content: flex-start;
  }
}
</style>
