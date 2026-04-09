<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="$emit('update:visible', $event)"
    :title="dialogTitle"
    width="640px"
    class="memo-dialog"
    :append-to-body="true"
  >
    <el-form :model="form" label-position="top" class="memo-dialog__form">
      <el-form-item label="所属文件夹">
        <el-select v-model="form.folderId" placeholder="请选择文件夹" style="width: 100%">
          <el-option v-for="folder in folders" :key="folder.id" :label="folder.name" :value="folder.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="周记录标题">
        <el-input v-model="form.title" placeholder="请输入周记录标题" />
      </el-form-item>
      <div class="memo-dialog__grid">
        <el-form-item label="周开始日期">
          <el-date-picker v-model="form.weekStartDate" value-format="YYYY-MM-DD" type="date" placeholder="选择开始日期" style="width: 100%" />
        </el-form-item>
        <el-form-item label="周结束日期">
          <el-date-picker v-model="form.weekEndDate" value-format="YYYY-MM-DD" type="date" placeholder="选择结束日期" style="width: 100%" />
        </el-form-item>
      </div>
      <div class="memo-dialog__grid">
        <el-form-item label="状态">
          <el-select v-model="form.status" style="width: 100%">
            <el-option label="草稿" value="draft" />
            <el-option label="已生成" value="generated" />
            <el-option label="已归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="摘要内容">
          <el-input v-model="form.summaryContent" placeholder="可选：保存已有周报摘要" />
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
  folders: {
    type: Array,
    default: () => []
  },
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:visible', 'submit'])

const form = reactive({
  folderId: null,
  title: '',
  weekStartDate: '',
  weekEndDate: '',
  status: 'draft',
  summaryContent: ''
})

watch(
  () => [props.visible, props.modelValue],
  () => {
    Object.assign(form, {
      folderId: props.modelValue?.folderId ?? (props.folders[0]?.id || null),
      title: props.modelValue?.title || '',
      weekStartDate: props.modelValue?.weekStartDate || '',
      weekEndDate: props.modelValue?.weekEndDate || '',
      status: props.modelValue?.status || 'draft',
      summaryContent: props.modelValue?.summaryContent || ''
    })
  },
  { immediate: true, deep: true }
)

const dialogTitle = computed(() => (props.mode === 'edit' ? '编辑周记录' : '新建周记录'))

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
.memo-dialog__footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
