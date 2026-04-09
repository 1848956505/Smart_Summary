<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="dialogTitle"
    width="520px"
    class="memo-dialog"
    :append-to-body="true"
  >
    <el-form :model="form" label-position="top" class="memo-dialog__form">
      <el-form-item label="文件夹名称">
        <el-input v-model="form.name" placeholder="请输入文件夹名称" />
      </el-form-item>
      <div class="memo-dialog__grid">
        <el-form-item label="排序值">
          <el-input-number v-model="form.sortOrder" :min="0" :step="1" controls-position="right" class="memo-dialog__number" />
        </el-form-item>
        <el-form-item label="默认折叠">
          <el-switch v-model="form.isCollapsed" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="memo-dialog__footer">
        <el-button @click="$emit('update:visible', false)">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">确定</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'create'
  },
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'submit'])

const form = reactive({
  name: '',
  sortOrder: 0,
  isCollapsed: 0
})

watch(
  () => [props.visible, props.modelValue],
  () => {
    Object.assign(form, {
      name: props.modelValue?.name || '',
      sortOrder: props.modelValue?.sortOrder ?? 0,
      isCollapsed: props.modelValue?.isCollapsed ?? 0
    })
  },
  { immediate: true, deep: true }
)

const dialogTitle = computed(() => (props.mode === 'edit' ? '编辑文件夹' : '新建文件夹'))

const handleSubmit = () => {
  emit('submit', { ...form })
}
</script>

<style scoped>
.memo-dialog__form {
  padding-top: 6px;
}
.memo-dialog__grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.memo-dialog__number {
  width: 100%;
}
.memo-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
