<template>
  <el-button :class="buttonClass" v-bind="$attrs" :type="type" :size="size" :loading="loading" :disabled="disabled">
    <slot />
  </el-button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  type: {
    type: String,
    default: 'default'
  },
  size: {
    type: String,
    default: 'default'
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: 'default'
  }
})

const buttonClass = computed(() => ['app-button', `app-button--${props.variant}`])
</script>

<style scoped>
.app-button {
  border-radius: var(--app-radius-md);
  font-weight: 600;
}

.app-button--default {}
.app-button--primary {}
.app-button--ghost {}
.app-button--danger {}
</style>
