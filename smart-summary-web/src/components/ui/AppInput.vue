<template>
  <el-input v-bind="$attrs" class="app-input" />
</template>

<style scoped>
.app-input :deep(.el-input__wrapper) {
  min-height: 32px;
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-border-default);
  background: var(--app-surface-elevated-strong);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.app-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--app-accent-border-strong);
  box-shadow: 0 0 0 3px var(--app-accent-soft);
}

.app-input :deep(.el-input__inner) {
  color: var(--app-color-text);
}
</style>
