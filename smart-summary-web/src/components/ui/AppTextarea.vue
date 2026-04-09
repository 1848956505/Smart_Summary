<template>
  <el-input v-bind="$attrs" type="textarea" class="app-textarea" />
</template>

<style scoped>
.app-textarea :deep(.el-textarea__inner) {
  border-radius: var(--app-radius-lg);
  border: 1px solid var(--app-color-border);
  box-shadow: none;
}
</style>
