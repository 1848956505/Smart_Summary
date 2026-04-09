<template>
  <el-table v-bind="$attrs" class="app-table" />
</template>

<style scoped>
.app-table :deep(.el-table__header-wrapper th) {
  background: var(--app-panel-bg-soft);
  color: var(--app-color-text-strong);
}
</style>
