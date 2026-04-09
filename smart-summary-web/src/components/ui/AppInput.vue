<template>
  <el-input v-bind="$attrs" class="app-input" />
</template>

<style scoped>
.app-input :deep(.el-input__wrapper) {
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-color-border);
}
</style>
