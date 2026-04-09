<template>
  <el-dialog v-model="open" :title="title" :width="width" :append-to-body="true" :close-on-click-modal="false" class="app-dialog">
    <slot />
    <template #footer>
      <slot name="footer" />
    </template>
  </el-dialog>
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
  width: {
    type: [String, Number],
    default: '720px'
  }
})

const emit = defineEmits(['update:visible'])

const open = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})
</script>
