<template>
  <div class="memo-workspace">
    <MemoSidebar
      :folders="folders"
      :weeks-by-folder="weeksByFolder"
      :selected-folder-id="selectedFolderId"
      :selected-week-id="selectedWeekId"
      :collapsed="sidebarCollapsed"
      @create-folder="openCreateFolderDialog"
      @toggle-sidebar="sidebarCollapsed = !sidebarCollapsed"
      @toggle-folder="handleToggleFolder"
      @select-folder="handleSelectFolder"
      @rename-folder="openEditFolderDialog"
      @delete-folder="handleDeleteFolder"
      @create-week="openCreateWeekDialog"
      @select-week="handleSelectWeek"
      @rename-week="openEditWeekDialog"
      @delete-week="handleDeleteWeek"
    />

    <section class="memo-workspace__content">
      <WeekRecordHeader
        :current-week="currentWeek"
        :stats="stats"
        :generating="generating"
        @generate="handleGenerateSummary"
        @save="handleSaveSummary"
        @copy="handleCopySummary"
        @export-markdown="handleExportMarkdown"
        @export-pdf="handleExportPdf"
        @archive="handleArchive"
        @open-stats="statsDrawerVisible = true"
      />

      <div v-if="currentWeek" class="memo-workspace__filters">
        <el-select v-model="filters.status" size="small" style="width: 130px">
          <el-option label="全部状态" value="all" />
          <el-option label="待办" value="todo" />
          <el-option label="进行中" value="doing" />
          <el-option label="已完成" value="done" />
          <el-option label="阻塞" value="blocked" />
        </el-select>
        <el-select v-model="filters.tag" size="small" style="width: 150px">
          <el-option label="全部标签" value="all" />
          <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
        </el-select>
        <el-input v-model="filters.keyword" size="small" clearable placeholder="搜索标题或内容" style="width: 240px" />
        <el-select v-model="activeDate" size="small" style="width: 130px" @change="handleSelectDate">
          <el-option
            v-for="day in weekNavigationOptions"
            :key="day.date"
            :label="day.label"
            :value="day.date"
          />
        </el-select>
        <el-button size="small" text @click="jumpToDefaultDate">
          <el-icon><Calendar /></el-icon>
          默认
        </el-button>
      </div>

      <div v-if="currentWeek" class="memo-workspace__body">
        <div class="memo-workspace__records-shell" ref="recordsShellRef">
          <DailyFragmentList
            :fragments="fragments"
            :week-start-date="currentWeek.weekStartDate"
            :week-end-date="currentWeek.weekEndDate"
            :active-date="activeDate"
            :status-filter="filters.status"
            :tag-filter="filters.tag"
            :keyword="filters.keyword"
            @edit-fragment="openEditFragmentDialog"
            @delete-fragment="handleDeleteFragment"
            @move-up="handleMoveUp"
            @move-down="handleMoveDown"
            @reorder-day="handleReorderDay"
            @select-date="handleSelectDate"
          />
        </div>
      </div>

      <MemoQuickComposer
        v-if="currentWeek"
        v-model="quickText"
        :active-date="activeDate"
        placeholder="记下此刻的工作碎片..."
        @submit="handleQuickSubmit"
        @open-detail="openCreateFragmentDialog(activeDate)"
        @jump-today="jumpToDefaultDate"
      />

      <div v-else class="memo-workspace__empty">
        <el-empty description="请选择或创建周记录" :image-size="88">
          <el-button type="primary" @click="openCreateFolderDialog">新建文件夹</el-button>
        </el-empty>
      </div>
    </section>

    <MemoFolderDialog
      v-model:visible="folderDialog.visible"
      :mode="folderDialog.mode"
      :loading="folderDialog.loading"
      :model-value="folderDialog.draft"
      @submit="submitFolderDialog"
    />

    <MemoWeekDialog
      v-model:visible="weekDialog.visible"
      :mode="weekDialog.mode"
      :loading="weekDialog.loading"
      :folders="folders"
      :model-value="weekDialog.draft"
      @submit="submitWeekDialog"
    />

    <MemoFragmentDialog
      v-model:visible="fragmentDialog.visible"
      :mode="fragmentDialog.mode"
      :loading="fragmentDialog.loading"
      :model-value="fragmentDialog.draft"
      @submit="submitFragmentDialog"
    />

    <el-drawer
      v-model="statsDrawerVisible"
      title="本周统计"
      size="420px"
      append-to-body
      :with-header="true"
    >
      <WeeklyStatsPanel :fragments="fragments" />
    </el-drawer>
  </div>
</template>

<script setup>
import MemoSidebar from '@/components/memo/MemoSidebar.vue'
import WeekRecordHeader from '@/components/memo/WeekRecordHeader.vue'
import DailyFragmentList from '@/components/memo/DailyFragmentList.vue'
import WeeklyStatsPanel from '@/components/memo/WeeklyStatsPanel.vue'
import MemoQuickComposer from '@/components/memo/MemoQuickComposer.vue'
import MemoFolderDialog from '@/components/memo/MemoFolderDialog.vue'
import MemoWeekDialog from '@/components/memo/MemoWeekDialog.vue'
import MemoFragmentDialog from '@/components/memo/MemoFragmentDialog.vue'
import { useMemoWorkspace } from '@/views/memos/useMemoWorkspace'
import { Calendar } from '@element-plus/icons-vue'

const {
  folders,
  weeksByFolder,
  selectedFolderId,
  selectedWeekId,
  currentWeek,
  fragments,
  quickText,
  generating,
  statsDrawerVisible,
  sidebarCollapsed,
  activeDate,
  filters,
  folderDialog,
  weekDialog,
  fragmentDialog,
  recordsShellRef,
  stats,
  availableTags,
  weekNavigationOptions,
  handleSelectDate,
  jumpToDefaultDate,
  handleToggleFolder,
  handleSelectFolder,
  openCreateFolderDialog,
  openEditFolderDialog,
  submitFolderDialog,
  handleDeleteFolder,
  openCreateWeekDialog,
  openEditWeekDialog,
  submitWeekDialog,
  handleDeleteWeek,
  handleSelectWeek,
  openCreateFragmentDialog,
  openEditFragmentDialog,
  submitFragmentDialog,
  handleQuickSubmit,
  handleDeleteFragment,
  handleMoveUp,
  handleMoveDown,
  handleReorderDay,
  handleGenerateSummary,
  handleSaveSummary,
  handleArchive,
  handleCopySummary,
  handleExportMarkdown,
  handleExportPdf
} = useMemoWorkspace()
</script>

<style scoped>
.memo-workspace {
  display: flex;
  gap: 18px;
  min-height: 100%;
  height: calc(100% + var(--app-space-6) * 2);
  width: calc(100% + var(--app-space-6) * 2);
  margin: calc(var(--app-space-6) * -1);
  overflow: hidden;
}

.memo-workspace__content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
  overflow: hidden;
}

.memo-workspace__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 0 2px;
}

.memo-workspace__body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 0;
  flex: 1;
  align-items: stretch;
  overflow: hidden;
}

.memo-workspace__records-shell {
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding-right: 4px;
}

.memo-workspace__empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

@media (max-width: 1300px) {
  .memo-workspace {
    flex-direction: column;
    overflow: hidden;
  }
}

@media (max-width: 1100px) {
  .memo-workspace__body {
    flex-direction: column;
  }
}

.memo-workspace__content :deep(.memo-composer) {
  margin-top: 2px;
}
</style>
