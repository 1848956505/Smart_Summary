<template>
  <el-dropdown v-bind="$attrs" :popper-class="popperClass" class="app-dropdown">
    <slot />
    <template v-if="$slots.dropdown" #dropdown>
      <slot name="dropdown" />
    </template>
  </el-dropdown>
</template>

<script setup>
import { computed, useAttrs } from 'vue'

const attrs = useAttrs()

const popperClass = computed(() => {
  const incoming = attrs.popperClass || attrs['popper-class'] || ''
  return `${incoming} app-overlay-popper app-dropdown-popper`.trim()
})
</script>

<style scoped>
.app-dropdown :deep(.el-tooltip__trigger:focus-visible) {
  outline: 2px solid var(--app-accent-border-strong);
  outline-offset: 2px;
  border-radius: var(--app-radius-sm);
}
</style>
