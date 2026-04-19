<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="dialogTitle"
    width="760px"
    class="memo-dialog"
    :append-to-body="true"
    align-center
  >
    <el-form :model="form" label-position="top" class="memo-dialog__form">
      <div class="memo-dialog__grid">
        <el-form-item label="工作日期">
          <el-date-picker v-model="form.workDate" value-format="YYYY-MM-DD" type="date" placeholder="选择日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="排序值">
          <el-input-number v-model="form.sortOrder" :min="0" :step="1" controls-position="right" class="memo-dialog__number" />
        </el-form-item>
      </div>
      <el-form-item label="标题">
        <el-input v-model="form.title" placeholder="请输入碎片标题" />
      </el-form-item>
      <el-form-item label="内容">
        <el-input v-model="form.content" type="textarea" :rows="6" placeholder="填写碎片的具体内容" />
      </el-form-item>
      <div class="memo-dialog__grid">
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="doing" />
            <el-option label="已完成" value="done" />
            <el-option label="阻塞" value="blocked" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="form.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
          </el-select>
        </el-form-item>
      </div>
      <el-form-item label="标签">
        <el-input v-model="form.tag" placeholder="例如：开发 / 测试 / 会议 / 设计" />
      </el-form-item>
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
  id: null,
  weekRecordId: null,
  workDate: '',
  title: '',
  content: '',
  status: 'todo',
  priority: 'medium',
  tag: '未分类',
  sortOrder: 0
})

watch(
  () => [props.visible, props.modelValue],
  () => {
    Object.assign(form, {
      id: props.modelValue?.id ?? null,
      weekRecordId: props.modelValue?.weekRecordId ?? null,
      workDate: props.modelValue?.workDate || '',
      title: props.modelValue?.title || '',
      content: props.modelValue?.content || '',
      status: props.modelValue?.status || 'todo',
      priority: props.modelValue?.priority || 'medium',
      tag: props.modelValue?.tag || '未分类',
      sortOrder: props.modelValue?.sortOrder ?? 0
    })
  },
  { immediate: true, deep: true }
)

const dialogTitle = computed(() => (props.mode === 'edit' ? '编辑碎片' : '新增碎片'))

const handleSubmit = () => {
  emit('submit', { ...form })
}
</script>

<style scoped>
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
