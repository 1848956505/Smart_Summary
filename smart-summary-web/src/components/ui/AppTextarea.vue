<template>
  <el-input v-bind="$attrs" type="textarea" class="app-textarea" />
</template>

<style scoped>
.app-textarea :deep(.el-textarea__inner) {
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-border-default);
  box-shadow: none;
  background: var(--app-surface-elevated-strong);
  color: var(--app-color-text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.app-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--app-accent-border-strong);
  box-shadow: 0 0 0 3px var(--app-accent-soft);
}
</style>
