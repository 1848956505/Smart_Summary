<template>
  <aside :class="['app-sidebar', { 'app-sidebar--collapsed': collapsed }]">
    <div class="app-sidebar__brand">
      <div class="app-sidebar__logo">S</div>
      <div class="app-sidebar__brand-text">
        <h2>Smart Summary</h2>
        <p>Enterprise Workspace</p>
      </div>
    </div>

    <button class="app-sidebar__collapse" @click="$emit('toggle')">
      <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
      <span>收起导航</span>
    </button>

    <nav class="app-sidebar__nav">
      <button
        v-for="item in menuItems"
        :key="item.key"
        :class="['app-sidebar__item', { 'app-sidebar__item--active': activeKey === item.key }]"
        @click="$emit('select', item.key)"
      >
        <el-icon class="app-sidebar__icon"><component :is="item.icon" /></el-icon>
        <span class="app-sidebar__label">{{ item.label }}</span>
      </button>
    </nav>

    <div class="app-sidebar__footer">
      <div class="app-sidebar__user">
        <div class="app-sidebar__avatar">{{ userAvatar }}</div>
        <div class="app-sidebar__user-info">
          <p class="app-sidebar__name">{{ displayUsername }}</p>
          <p class="app-sidebar__meta">{{ userPosition || '企业协作空间' }}</p>
        </div>
      </div>

      <div class="app-sidebar__actions">
        <button class="app-sidebar__settings" @click="$emit('openSettings')">
          <el-icon><Setting /></el-icon>
          <span>系统偏好设置</span>
        </button>
        <button class="app-sidebar__logout" @click="$emit('logout')">
          <el-icon><SwitchButton /></el-icon>
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { Fold, Expand, SwitchButton, Setting } from '@element-plus/icons-vue'

defineProps({
  collapsed: Boolean,
  menuItems: { type: Array, default: () => [] },
  activeKey: { type: String, default: '' },
  username: { type: String, default: 'User' },
  displayUsername: { type: String, default: 'User' },
  userPosition: { type: String, default: '' },
  userAvatar: { type: String, default: 'U' }
})

defineEmits(['toggle', 'select', 'logout', 'openSettings'])
</script>

<style scoped>
.app-sidebar {
  width: var(--app-sidebar-width);
  min-width: var(--app-sidebar-width);
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: var(--app-space-4);
  border-radius: var(--app-radius-2xl);
  background: var(--app-panel-bg);
  border: 1px solid var(--app-panel-border);
  box-shadow: var(--app-panel-shadow);
  overflow: hidden;
  transition: width 0.3s ease, min-width 0.3s ease, padding 0.3s ease;
}

.app-sidebar--collapsed {
  width: var(--app-sidebar-collapsed);
  min-width: var(--app-sidebar-collapsed);
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--app-space-3);
  min-height: 72px;
  padding: var(--app-space-2) var(--app-space-2) var(--app-space-4);
}

.app-sidebar__logo {
  width: 44px;
  height: 44px;
  border-radius: var(--app-radius-md);
  display: grid;
  place-items: center;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.app-sidebar__brand-text h2 {
  font-size: 16px;
  font-weight: 800;
  margin: 0;
  color: var(--app-color-text-strong);
}

.app-sidebar__brand-text p {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.app-sidebar__brand-text,
.app-sidebar__label,
.app-sidebar__settings span,
.app-sidebar__logout span,
.app-sidebar__user-info {
  max-width: 220px;
  overflow: hidden;
  white-space: nowrap;
  transition: opacity 0.24s ease, transform 0.24s ease, max-width 0.3s ease;
}

.app-sidebar__collapse,
.app-sidebar__item,
.app-sidebar__settings,
.app-sidebar__logout {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  border-radius: var(--app-radius-md);
  padding: 12px 14px;
  color: var(--app-color-text-soft);
  background: transparent;
  transition: background-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.app-sidebar__collapse:hover,
.app-sidebar__item:hover,
.app-sidebar__settings:hover,
.app-sidebar__logout:hover {
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
}

.app-sidebar__nav {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: var(--app-space-2) 0;
  overflow: auto;
}

.app-sidebar__item--active {
  background: var(--app-color-primary-soft);
  color: var(--app-color-primary-strong);
  font-weight: 700;
}

.app-sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-3);
  padding-top: var(--app-space-4);
  border-top: 1px solid var(--app-panel-border);
}

.app-sidebar__user {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--app-radius-lg);
  background: var(--app-panel-bg-soft);
  border: 1px solid var(--app-panel-border);
}

.app-sidebar__avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.app-sidebar__user-info {
  min-width: 0;
}

.app-sidebar__name {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
  color: var(--app-color-text-strong);
}

.app-sidebar__meta {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--app-color-text-muted);
}

.app-sidebar__actions {
  display: grid;
  gap: 8px;
}

.app-sidebar__settings,
.app-sidebar__logout {
  justify-content: flex-start;
  padding: 10px 12px;
}

.app-sidebar--collapsed .app-sidebar__brand-text,
.app-sidebar--collapsed .app-sidebar__label,
.app-sidebar--collapsed .app-sidebar__settings span,
.app-sidebar--collapsed .app-sidebar__logout span,
.app-sidebar--collapsed .app-sidebar__user-info {
  max-width: 0;
  opacity: 0;
  transform: translateX(-8px);
}

.app-sidebar--collapsed .app-sidebar__brand,
.app-sidebar--collapsed .app-sidebar__collapse,
.app-sidebar--collapsed .app-sidebar__item,
.app-sidebar--collapsed .app-sidebar__settings,
.app-sidebar--collapsed .app-sidebar__logout {
  justify-content: center;
}

@media (max-width: 1200px) {
  .app-sidebar,
  .app-sidebar--collapsed {
    width: 100%;
    min-width: 0;
  }
}
</style>
