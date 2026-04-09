<template>
  <el-dialog v-model="open" :title="title" :width="width" :append-to-body="true" class="app-confirm-dialog">
    <p class="app-confirm-dialog__content">{{ content }}</p>
    <template #footer>
      <div class="app-confirm-dialog__footer">
        <el-button @click="open = false">取消</el-button>
        <el-button type="danger" :loading="loading" @click="$emit('confirm')">确认</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  title: { type: String, default: '确认操作' },
  content: { type: String, default: '确认继续吗？' },
  width: { type: [String, Number], default: '480px' },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['update:visible', 'confirm'])

const open = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value)
})
</script>

<style scoped>
.app-confirm-dialog__content {
  margin: 0;
  color: var(--app-color-text-soft);
  line-height: 1.8;
}

.app-confirm-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
