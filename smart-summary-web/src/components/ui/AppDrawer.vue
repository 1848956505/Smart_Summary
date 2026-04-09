<template>
  <el-drawer v-model="open" :title="title" :size="size" :append-to-body="true" :destroy-on-close="true" class="app-drawer">
    <slot />
    <template #footer>
      <slot name="footer" />
    </template>
  </el-drawer>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: [String, Number],
    default: '40%'
  }
})

const emit = defineEmits(['update:visible'])

const open = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})
</script>
