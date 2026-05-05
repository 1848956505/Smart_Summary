<template>
  <el-select v-bind="$attrs" :popper-class="popperClass" class="app-select">
    <slot />
  </el-select>
</template>

<script setup>
import { computed, useAttrs } from 'vue'

const attrs = useAttrs()

const popperClass = computed(() => {
  const incoming = attrs.popperClass || attrs['popper-class'] || ''
  return `${incoming} app-overlay-popper app-select-popper`.trim()
})
</script>

<style scoped>
.app-select :deep(.el-input__wrapper) {
  border-radius: var(--app-radius-md);
  box-shadow: none;
  border: 1px solid var(--app-border-default);
}
</style>
