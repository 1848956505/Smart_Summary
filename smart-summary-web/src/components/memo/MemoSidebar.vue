<template>
  <aside class="memo-sidebar">
    <div class="memo-sidebar__top">
      <div>
        <p class="memo-sidebar__eyebrow">Memo Studio</p>
        <h3>碎片记录本</h3>
      </div>
    </div>

    <div class="memo-sidebar__tree">
      <div v-for="folder in folders" :key="folder.id" class="folder-block">
        <div class="folder-row" :class="{ active: selectedFolderId === folder.id }">
          <button class="folder-toggle" @click="$emit('toggle-folder', folder)">
            <el-icon :size="14">
              <CaretRight v-if="folder.isCollapsed" />
              <CaretBottom v-else />
            </el-icon>
          </button>
          <div class="folder-main" @click="$emit('select-folder', folder)">
            <span class="folder-name">{{ folder.name }}</span>
            <span class="folder-meta">{{ (weeksByFolder[folder.id] || []).length }} 个周记录</span>
          </div>
          <div class="folder-actions">
            <el-button text size="small" @click="$emit('create-week', folder.id)">
              <el-icon><Plus /></el-icon>
            </el-button>
            <el-dropdown trigger="click">
              <span class="el-dropdown-link">⋯</span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="$emit('rename-folder', folder)">重命名</el-dropdown-item>
                  <el-dropdown-item @click="$emit('delete-folder', folder)">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>

        <div v-if="!folder.isCollapsed" class="weeks-list">
          <div
            v-for="weekRecord in weeksByFolder[folder.id] || []"
            :key="weekRecord.id"
            class="week-row"
            :class="{ selected: selectedWeekId === weekRecord.id }"
            @click="$emit('select-week', weekRecord)"
          >
            <div class="week-main">
              <span class="week-title">{{ weekRecord.title }}</span>
              <span class="week-range">{{ weekRecord.weekStartDate }} ~ {{ weekRecord.weekEndDate }}</span>
            </div>
            <div class="week-meta">
              <el-tag size="small" :type="statusType(weekRecord.status)">
                {{ statusLabel(weekRecord.status) }}
              </el-tag>
              <span class="week-count">{{ weekRecord.fragmentCount || 0 }} 条</span>
              <el-dropdown trigger="click" @click.stop>
                <span class="el-dropdown-link">⋯</span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="$emit('rename-week', weekRecord)">重命名周记录</el-dropdown-item>
                    <el-dropdown-item @click="$emit('delete-week', weekRecord)">删除周记录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="memo-sidebar__footer">
      <el-button class="memo-sidebar__create-btn" @click="$emit('create-folder')">
        <el-icon><FolderAdd /></el-icon>
        新建文件夹
      </el-button>
    </div>
  </aside>
</template>

<script setup>
import { CaretRight, CaretBottom, Plus, FolderAdd } from '@element-plus/icons-vue'

defineProps({
  folders: { type: Array, default: () => [] },
  weeksByFolder: { type: Object, default: () => ({}) },
  selectedFolderId: { type: Number, default: null },
  selectedWeekId: { type: Number, default: null }
})

defineEmits(['create-folder', 'toggle-folder', 'select-folder', 'rename-folder', 'delete-folder', 'create-week', 'select-week', 'rename-week', 'delete-week'])

const statusType = (status) => {
  if (status === 'generated') return 'success'
  if (status === 'archived') return 'info'
  return 'warning'
}

const statusLabel = (status) => {
  if (status === 'generated') return '已生成'
  if (status === 'archived') return '已归档'
  return '草稿'
}
</script>

<style scoped>
.memo-sidebar {
  width: 340px;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: var(--app-panel-bg);
  border: 1px solid var(--app-panel-border);
  border-radius: var(--app-radius-2xl);
  box-shadow: var(--app-panel-shadow);
  overflow: hidden;
  min-height: 0;
}

.memo-sidebar__top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.memo-sidebar__eyebrow {
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.memo-sidebar__top h3 {
  margin-top: 6px;
  font-size: 20px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.memo-sidebar__tree {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-right: 4px;
  min-height: 0;
}

.memo-sidebar__footer {
  margin-top: auto;
}

.memo-sidebar__create-btn {
  width: 100%;
  height: 44px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(79, 70, 229, 0.12));
  border-color: rgba(37, 99, 235, 0.14);
  color: var(--app-color-primary-strong);
  font-weight: 700;
}

.folder-block {
  border-radius: var(--app-radius-xl);
  background: var(--app-panel-bg-soft);
  border: 1px solid var(--app-color-border);
  overflow: hidden;
}

.folder-row {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px;
  transition: background-color 0.2s ease;
}

.folder-row.active {
  background: var(--app-color-primary-soft);
}

.folder-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: #fff;
  color: var(--app-color-text-muted);
  flex-shrink: 0;
}

.folder-main {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.folder-name {
  display: block;
  font-size: 14px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-meta {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.folder-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.weeks-list {
  border-top: 1px solid var(--app-color-border);
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.week-row {
  border-radius: 18px;
  padding: 12px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  background: #fff;
  border: 1px solid var(--app-color-border);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.week-row:hover {
  transform: translateY(-1px);
  border-color: rgba(37, 99, 235, 0.24);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.week-row.selected {
  border-color: rgba(37, 99, 235, 0.32);
  background: var(--app-color-primary-soft);
}

.week-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.week-title {
  font-size: 13px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.week-range {
  margin-top: 5px;
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.week-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.week-count {
  font-size: 12px;
  color: var(--app-color-text-soft);
}

@media (max-width: 1200px) {
  .memo-sidebar {
    width: 100%;
  }
}
</style>
