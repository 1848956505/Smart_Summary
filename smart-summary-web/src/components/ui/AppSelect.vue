<template>
  <el-select v-bind="$attrs" class="app-select" />
</template>

<style scoped>
.app-select :deep(.el-input__wrapper) {
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-color-border);
}
</style>
