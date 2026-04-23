<template>
  <aside :class="['app-sidebar', { 'app-sidebar--collapsed': collapsed }]">
    <div class="app-sidebar__shell">
      <div class="app-sidebar__brand">
        <div class="app-sidebar__mark">S</div>
        <div class="app-sidebar__brand-copy">
          <p class="app-sidebar__eyebrow">AI WORKSPACE</p>
          <h2>Smart Summary</h2>
          <p>记录碎片工作，高效生成总结</p>
        </div>
      </div>

      <button class="app-sidebar__collapse" type="button" @click="$emit('toggle')">
        <el-icon><Fold v-if="!collapsed" /><Expand v-else /></el-icon>
        <span class="app-sidebar__collapse-label">{{ collapsed ? '展开导航' : '收起导航' }}</span>
      </button>

      <nav class="app-sidebar__nav" aria-label="主导航">
        <button
          v-for="item in menuItems"
          :key="item.key"
          :class="['app-sidebar__item', { 'app-sidebar__item--active': activeKey === item.key }]"
          type="button"
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
            <p v-if="userPosition" class="app-sidebar__meta">{{ userPosition }}</p>
          </div>
        </div>

        <div class="app-sidebar__actions">
          <button class="app-sidebar__settings" type="button" @click="$emit('openSettings')">
            <el-icon><Setting /></el-icon>
            <span>系统设置</span>
          </button>
          <button class="app-sidebar__logout" type="button" @click="$emit('logout')">
            <el-icon><SwitchButton /></el-icon>
            <span>退出登录</span>
          </button>
        </div>
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
  displayUsername: { type: String, default: '用户' },
  userPosition: { type: String, default: '' },
  userAvatar: { type: String, default: 'U' }
})

defineEmits(['toggle', 'select', 'logout', 'openSettings'])
</script>

<style scoped>
.app-sidebar {
  width: var(--app-sidebar-width);
  min-width: var(--app-sidebar-width);
  margin-top: var(--app-space-5);
  height: calc(100vh - (var(--app-shell-gutter) * 2) - var(--app-space-5));
  display: flex;
  padding: 0;
  border-radius: var(--app-radius-2xl);
  background: var(--app-sidebar-bg);
  border: 1px solid var(--app-color-border-soft);
  box-shadow: none;
  backdrop-filter: blur(18px);
  overflow: hidden;
  transition: width 0.3s ease, min-width 0.3s ease;
}

.app-sidebar__shell {
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 12px;
}

.app-sidebar__brand {
  display: flex;
  align-items: center;
  gap: var(--app-space-3);
  padding: var(--app-space-2) var(--app-space-2) var(--app-space-3);
  min-height: 60px;
}

.app-sidebar__mark {
  width: 34px;
  height: 34px;
  border-radius: 11px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.04em;
  background: linear-gradient(135deg, var(--app-color-primary), var(--app-color-primary-strong));
  box-shadow: 0 10px 22px color-mix(in srgb, var(--app-color-primary) 30%, transparent);
  flex-shrink: 0;
}

.app-sidebar__brand-copy {
  min-width: 0;
}

.app-sidebar__eyebrow {
  margin: 0 0 3px;
  color: var(--app-color-text-muted);
  font-size: 10px;
  letter-spacing: 0.16em;
}

.app-sidebar__brand-copy h2 {
  margin: 0;
  color: var(--app-color-text-strong);
  font-size: 14px;
  line-height: 1.2;
  font-weight: var(--app-type-weight-bold);
}

.app-sidebar__brand-copy p:last-child {
  margin: 4px 0 0;
  color: var(--app-color-text-muted);
  font-size: 11px;
  line-height: 1.5;
}

.app-sidebar__brand-copy,
.app-sidebar__label,
.app-sidebar__collapse-label,
.app-sidebar__settings span,
.app-sidebar__logout span,
.app-sidebar__user-info {
  max-width: 190px;
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
  gap: 8px;
  width: 100%;
  border-radius: var(--app-radius-md);
  padding: 9px 10px;
  color: var(--app-color-text-soft);
  background: transparent;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.app-sidebar__collapse:hover,
.app-sidebar__item:hover,
.app-sidebar__settings:hover,
.app-sidebar__logout:hover {
  background: var(--app-sidebar-hover-bg);
  color: var(--app-color-text-strong);
}

.app-sidebar__collapse {
  justify-content: flex-start;
  margin-top: var(--app-space-2);
  margin-bottom: var(--app-space-3);
  border: 1px solid var(--app-color-border-soft);
  background: var(--app-sidebar-soft-bg);
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
  background: var(--app-sidebar-active-bg);
  color: var(--app-color-text-strong);
  font-weight: 700;
}

.app-sidebar__footer {
  display: flex;
  flex-direction: column;
  gap: var(--app-space-3);
  padding-top: var(--app-space-4);
  border-top: 1px solid var(--app-color-border-soft);
}

.app-sidebar__user {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: var(--app-radius-lg);
  background: var(--app-sidebar-soft-bg);
  border: 1px solid var(--app-color-border-soft);
}

.app-sidebar__avatar {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  background: var(--app-gradient-primary);
  color: #fff;
  font-weight: 800;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.app-sidebar__name {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  color: var(--app-color-text-strong);
}

.app-sidebar__meta {
  margin: 2px 0 0;
  font-size: 10px;
  color: var(--app-color-text-muted);
}

.app-sidebar__actions {
  display: grid;
  gap: 8px;
}

.app-sidebar__settings,
.app-sidebar__logout {
  justify-content: flex-start;
  padding: 8px 10px;
}

.app-sidebar--collapsed {
  width: var(--app-sidebar-collapsed);
  min-width: var(--app-sidebar-collapsed);
}

.app-sidebar--collapsed .app-sidebar__shell {
  padding-inline: var(--app-space-3);
}

.app-sidebar--collapsed .app-sidebar__brand {
  justify-content: center;
}

.app-sidebar--collapsed .app-sidebar__brand-copy,
.app-sidebar--collapsed .app-sidebar__label,
.app-sidebar--collapsed .app-sidebar__collapse-label,
.app-sidebar--collapsed .app-sidebar__settings span,
.app-sidebar--collapsed .app-sidebar__logout span,
.app-sidebar--collapsed .app-sidebar__user-info {
  max-width: 0;
  opacity: 0;
  transform: translateX(-8px);
}

.app-sidebar--collapsed .app-sidebar__collapse,
.app-sidebar--collapsed .app-sidebar__item,
.app-sidebar--collapsed .app-sidebar__settings,
.app-sidebar--collapsed .app-sidebar__logout {
  justify-content: center;
}

.app-sidebar--collapsed .app-sidebar__collapse {
  padding-inline: 10px;
}

@media (max-width: 1200px) {
  .app-sidebar,
  .app-sidebar--collapsed {
    width: 100%;
    min-width: 0;
    margin-top: 0;
    height: auto;
  }

  .app-sidebar__shell {
    padding: var(--app-space-3);
  }
}
</style>

