<template>
  <section class="summary-panel app-surface">
    <div class="summary-panel__header">
      <div>
        <p class="summary-panel__eyebrow">Report Desk</p>
        <h3>周报结果</h3>
      </div>
      <span class="summary-panel__hint">支持二次编辑后保存</span>
    </div>

    <AppTextarea
      :model-value="summary"
      @update:model-value="$emit('update:summary', $event)"
      :rows="18"
      resize="none"
      placeholder="点击“一键生成周报”后，这里会出现结构化周报内容"
      class="summary-panel__editor"
    />
  </section>
</template>

<script setup>
import AppTextarea from '@/components/ui/AppTextarea.vue'

defineProps({ summary: { type: String, default: '' } })
defineEmits(['update:summary'])
</script>

<style scoped>
.summary-panel {
  padding: 18px;
  border-radius: var(--app-radius-2xl);
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.summary-panel__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex: 0 0 auto;
}

.summary-panel__eyebrow {
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.summary-panel h3 {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.summary-panel__hint {
  padding: 8px 12px;
  border-radius: 999px;
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  font-size: 12px;
  font-weight: 700;
}

.summary-panel__editor {
  flex: 1;
  min-height: 0;
}

.summary-panel__editor :deep(.el-textarea),
.summary-panel__editor :deep(.el-textarea__inner) {
  height: 100%;
}
</style>
