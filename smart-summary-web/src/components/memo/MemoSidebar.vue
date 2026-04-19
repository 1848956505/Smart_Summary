<template>
  <aside class="memo-sidebar" :class="{ 'memo-sidebar--collapsed': collapsed }">
    <div class="memo-sidebar__top">
      <div v-if="!collapsed" class="memo-sidebar__brand">
        <p class="memo-sidebar__eyebrow">碎片工作台</p>
        <div class="memo-sidebar__title-row">
          <h3>碎片记录本</h3>
          <span class="memo-sidebar__count">{{ folders.length }} 个文件夹</span>
        </div>
      </div>

      <button
        class="memo-button memo-button--ghost memo-button--icon memo-sidebar__collapse"
        type="button"
        :title="collapsed ? '展开目录' : '收起目录'"
        @click="$emit('toggle-sidebar')"
      >
        <el-icon>
          <CaretRight v-if="collapsed" />
          <CaretLeft v-else />
        </el-icon>
      </button>
    </div>

    <div v-if="!collapsed" class="memo-sidebar__tree">
      <div class="memo-sidebar__section-label">资料目录</div>

      <div v-for="folder in folders" :key="folder.id" class="folder-block">
        <div class="folder-row" :class="{ active: selectedFolderId === folder.id }">
          <button
            class="memo-button memo-button--ghost memo-button--icon folder-toggle"
            type="button"
            :title="folder.isCollapsed ? '展开周记录' : '收起周记录'"
            @click="$emit('toggle-folder', folder)"
          >
            <el-icon :size="14">
              <CaretRight v-if="folder.isCollapsed" />
              <CaretBottom v-else />
            </el-icon>
          </button>

          <button class="folder-main" type="button" @click="$emit('select-folder', folder)">
            <span class="folder-name">{{ folder.name }}</span>
            <span class="folder-meta">{{ (weeksByFolder[folder.id] || []).length }} 个周记录</span>
          </button>

          <div class="folder-actions">
            <button
              class="memo-button memo-button--ghost memo-button--icon"
              type="button"
              title="新建周记录"
              @click="$emit('create-week', folder.id)"
            >
              <el-icon><Plus /></el-icon>
            </button>
            <el-dropdown trigger="click">
              <button class="memo-button memo-button--ghost memo-button--icon memo-sidebar__more" type="button" title="更多操作" @click.stop>
                ...
              </button>
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
              <span class="week-range">{{ weekRecord.weekStartDate }} - {{ weekRecord.weekEndDate }}</span>
            </div>

            <div class="week-meta">
              <span :class="['memo-chip', 'memo-chip--state', statusChipClass(weekRecord.status)]">
                {{ statusLabel(weekRecord.status) }}
              </span>
              <div class="week-meta__bottom">
                <span class="week-count">{{ weekRecord.fragmentCount || 0 }} 条</span>
                <el-dropdown trigger="click" @click.stop>
                  <button class="memo-button memo-button--ghost memo-button--icon memo-sidebar__more" type="button" title="更多操作">
                    ...
                  </button>
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
    </div>

    <div v-else class="memo-sidebar__collapsed-view">
      <button
        class="memo-button memo-button--ghost memo-button--icon memo-sidebar__collapsed-action"
        type="button"
        title="展开目录"
        @click="$emit('toggle-sidebar')"
      >
        <el-icon><CaretRight /></el-icon>
      </button>
      <button
        class="memo-button memo-button--primary memo-button--icon memo-sidebar__collapsed-action"
        type="button"
        title="新建文件夹"
        @click="$emit('create-folder')"
      >
        <el-icon><FolderAdd /></el-icon>
      </button>
    </div>

    <div class="memo-sidebar__footer">
      <button class="memo-button memo-button--ghost memo-sidebar__create-btn" type="button" @click="$emit('create-folder')">
        <el-icon><FolderAdd /></el-icon>
        <span v-if="!collapsed">新建文件夹</span>
      </button>
    </div>
  </aside>
</template>

<script setup>
import { CaretRight, CaretLeft, CaretBottom, Plus, FolderAdd } from '@element-plus/icons-vue'

defineProps({
  folders: { type: Array, default: () => [] },
  weeksByFolder: { type: Object, default: () => ({}) },
  selectedFolderId: { type: Number, default: null },
  selectedWeekId: { type: Number, default: null },
  collapsed: { type: Boolean, default: false }
})

defineEmits([
  'create-folder',
  'toggle-sidebar',
  'toggle-folder',
  'select-folder',
  'rename-folder',
  'delete-folder',
  'create-week',
  'select-week',
  'rename-week',
  'delete-week'
])

const statusChipClass = (status) => {
  if (status === 'generated') return 'memo-chip--success'
  if (status === 'archived') return 'memo-chip--soft'
  return 'memo-chip--warning'
}

const statusLabel = (status) => {
  if (status === 'generated') return '已生成'
  if (status === 'archived') return '已归档'
  return '草稿'
}
</script>

<style scoped>
.memo-sidebar {
  width: 100%;
  min-width: 0;
  padding: 12px 12px 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: linear-gradient(180deg, var(--memo-surface-strong), var(--memo-surface-soft));
  border: 1px solid var(--memo-border);
  border-radius: var(--app-radius-2xl);
  box-shadow: var(--memo-shadow);
  min-height: calc(100vh - 48px);
  transition: padding 0.25s ease;
}

.memo-sidebar--collapsed {
  padding: 10px 7px;
}

.memo-sidebar__top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.memo-sidebar__brand {
  min-width: 0;
}

.memo-sidebar__eyebrow {
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.memo-sidebar__title-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.memo-sidebar__title-row h3 {
  font-size: 16px;
  font-weight: 800;
  color: var(--app-color-text-strong);
}

.memo-sidebar__count {
  font-size: 11px;
  color: var(--app-color-text-muted);
}

.memo-sidebar__tree {
  flex: 1;
  overflow: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 0;
}

.memo-sidebar__section-label {
  padding: 0 6px;
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--app-color-text-muted);
}

.memo-sidebar__collapsed-view {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 10px;
  padding-top: 4px;
}

.memo-sidebar__collapsed-action {
  width: 100%;
}

.memo-sidebar__footer {
  margin-top: auto;
  padding-top: 4px;
}

.memo-sidebar__create-btn {
  width: 100%;
  justify-content: center;
  gap: 8px;
}

.memo-sidebar--collapsed .memo-sidebar__create-btn {
  padding-inline: 0;
}

.memo-sidebar--collapsed .memo-sidebar__create-btn :deep(span) {
  display: none;
}

.folder-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.folder-row {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 8px 9px;
  border-radius: 14px;
  background: var(--memo-surface-muted);
  border: 1px solid transparent;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease;
}

.folder-row.active {
  background: var(--memo-accent-bg);
  border-color: var(--memo-border-strong);
  box-shadow: var(--memo-selected-shadow);
}

.folder-main {
  flex: 1;
  min-width: 0;
  text-align: left;
  background: transparent;
  border: 0;
  cursor: pointer;
}

.folder-name {
  display: block;
  font-size: 12px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.folder-meta {
  display: block;
  margin-top: 4px;
  font-size: 10px;
  color: var(--app-color-text-muted);
}

.folder-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.memo-sidebar__more {
  font-size: 16px;
  line-height: 1;
}

.weeks-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 14px;
  border-left: 1px solid var(--memo-line-soft);
  margin-left: 13px;
}

.week-row {
  border-radius: 14px;
  padding: 9px 10px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid var(--memo-border);
  box-shadow: var(--memo-shadow-soft);
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.week-row:hover,
.week-row.selected {
  background: var(--memo-accent-bg);
  border-color: var(--memo-border-strong);
  box-shadow: var(--memo-selected-shadow);
  transform: translateY(-1px);
}

.week-main {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.week-title {
  font-size: 11px;
  font-weight: 800;
  color: var(--app-color-text-strong);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.week-range {
  margin-top: 5px;
  font-size: 10px;
  color: var(--app-color-text-muted);
}

.week-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.week-meta__bottom {
  display: flex;
  align-items: center;
  gap: 6px;
}

.week-count {
  font-size: 10px;
  color: var(--app-color-text-soft);
}

@media (max-width: 1280px) {
  .memo-sidebar {
    min-height: auto;
  }
}
</style>
