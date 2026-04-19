<template>
  <div class="memo-workspace" :class="{ 'memo-workspace--rail-collapsed': sidebarCollapsed }">
    <aside class="memo-workspace__rail">
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
    </aside>

    <section class="memo-workspace__main">
      <WeekRecordHeader
        class="memo-workspace__context"
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

      <div v-if="currentWeek" class="memo-workspace__stage">
        <div class="memo-workspace__filters app-surface">
          <span class="memo-workspace__filters-label">筛选</span>

          <el-select v-model="filters.status" size="small" class="memo-workspace__select memo-workspace__control">
            <el-option label="全部状态" value="all" />
            <el-option label="待办" value="todo" />
            <el-option label="进行中" value="doing" />
            <el-option label="已完成" value="done" />
            <el-option label="阻塞" value="blocked" />
          </el-select>

          <el-select
            v-model="filters.tag"
            size="small"
            class="memo-workspace__select memo-workspace__select--wide memo-workspace__control"
          >
            <el-option label="全部标签" value="all" />
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>

          <el-input
            v-model="filters.keyword"
            size="small"
            clearable
            placeholder="搜索标题或内容"
            class="memo-workspace__search memo-workspace__control"
          />

          <el-select
            v-model="activeDate"
            size="small"
            class="memo-workspace__select memo-workspace__select--compact memo-workspace__control"
            @change="handleSelectDate"
          >
            <el-option
              v-for="day in weekNavigationOptions"
              :key="day.date"
              :label="day.label"
              :value="day.date"
            />
          </el-select>

          <el-button size="small" class="memo-button memo-button--ghost memo-workspace__jump" @click="jumpToDefaultDate">
            <el-icon><Calendar /></el-icon>
            今天
          </el-button>
        </div>

        <div class="memo-workspace__timeline-shell" ref="recordsShellRef">
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

      <div v-else class="memo-workspace__empty app-surface">
        <el-empty description="请选择或新建一条周记录" :image-size="88">
          <el-button class="memo-button memo-button--primary" @click="openCreateFolderDialog">新建文件夹</el-button>
        </el-empty>
      </div>

      <div v-if="currentWeek" class="memo-workspace__capture">
        <MemoQuickComposer
          v-model="quickText"
          :active-date="activeDate"
          placeholder="记下此刻的工作碎片..."
          @submit="handleQuickSubmit"
          @open-detail="openCreateFragmentDialog(activeDate)"
          @jump-today="jumpToDefaultDate"
        />
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
  display: grid;
  grid-template-columns: var(--memo-rail-width) minmax(0, 1fr);
  gap: var(--app-space-4);
  width: 100%;
  min-height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - (var(--app-space-5) * 2) - 2px);
  align-items: stretch;
}

.memo-workspace--rail-collapsed {
  grid-template-columns: var(--memo-rail-collapsed-width) minmax(0, 1fr);
}

.memo-workspace__rail {
  position: sticky;
  top: var(--app-space-4);
  align-self: start;
}

.memo-workspace__main {
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: var(--app-space-4);
}

.memo-workspace__stage {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  gap: var(--app-space-4);
}

.memo-workspace__filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  padding: 8px 10px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid var(--memo-border);
  box-shadow: 0 8px 20px rgba(39, 72, 124, 0.04);
}

.memo-workspace__filters-label {
  font-size: 10px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
  margin-right: 4px;
  padding-left: 2px;
}

.memo-workspace__select {
  width: 128px;
}

.memo-workspace__select--wide {
  width: 148px;
}

.memo-workspace__select--compact {
  width: 118px;
}

.memo-workspace__search {
  width: 220px;
}

.memo-workspace__jump {
  margin-left: -2px;
}

.memo-workspace__control :deep(.el-select__wrapper),
.memo-workspace__control :deep(.el-input__wrapper) {
  min-height: 30px;
  border-radius: 10px;
  box-shadow: none;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid var(--memo-button-border);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.memo-workspace__control :deep(.el-select__wrapper.is-focused),
.memo-workspace__control :deep(.el-input__wrapper.is-focus) {
  border-color: var(--memo-border-strong);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
}

.memo-workspace__control :deep(.el-input__inner),
.memo-workspace__control :deep(.el-select__placeholder),
.memo-workspace__control :deep(.el-select__selected-item) {
  font-size: 11px;
  color: var(--app-color-text);
}

.memo-workspace__control :deep(.el-input__inner::placeholder) {
  color: var(--app-color-text-muted);
}

.memo-workspace__timeline-shell {
  min-height: 0;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-right: 4px;
  scrollbar-gutter: stable;
}

.memo-workspace__capture {
  position: sticky;
  bottom: var(--app-space-4);
  z-index: 2;
  margin-top: var(--app-space-2);
}

.memo-workspace__empty {
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--app-radius-2xl);
}

@media (max-width: 1280px) {
  .memo-workspace,
  .memo-workspace--rail-collapsed {
    grid-template-columns: minmax(0, 1fr);
  }

  .memo-workspace__rail {
    position: static;
  }
}

@media (max-width: 860px) {
  .memo-workspace__filters {
    order: 2;
    padding: 10px;
  }

  .memo-workspace__search,
  .memo-workspace__select,
  .memo-workspace__select--wide,
  .memo-workspace__select--compact {
    width: 100%;
  }

  .memo-workspace__timeline-shell {
    order: 1;
  }

  .memo-workspace__capture {
    position: static;
  }
}
</style>
