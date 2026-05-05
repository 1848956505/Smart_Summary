<template>
  <el-date-picker v-bind="$attrs" :popper-class="popperClass" class="app-date-picker" />
</template>

<script setup>
import { computed, useAttrs } from 'vue'

const attrs = useAttrs()

const popperClass = computed(() => {
  const incoming = attrs.popperClass || attrs['popper-class'] || ''
  return `${incoming} app-overlay-popper app-datepicker-popper`.trim()
})
</script>

<style scoped>
.app-date-picker {
  width: 100%;
}

.app-date-picker :deep(.el-input__wrapper) {
  min-height: 32px;
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-border-default);
  background: var(--app-surface-elevated-strong);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.app-date-picker :deep(.el-input__wrapper.is-focus) {
  border-color: var(--app-accent-border-strong);
  box-shadow: 0 0 0 3px var(--app-accent-soft);
}

.app-date-picker :deep(.el-input__inner) {
  color: var(--app-color-text);
}
</style>
