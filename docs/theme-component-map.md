# 主题组件映射（可一键换肤）

本文档用于说明当前前端中，哪些组件已经归类到统一样式库，以及应该到哪里改主题变量。

## 1. 主按钮（Primary Action）

- 典型场景：
  - 工作台 `开始生成`
  - 智能生成 `生成周报`
  - 碎片记录本 `一键生成周报`
  - 快速输入区发送按钮
- 统一样式入口：
  - 组件类：`AppButton` 的 `primary` 变体（`src/components/ui/AppButton.vue`）
  - 兼容类：`.memo-button--primary`（`src/styles/components.css`）
- 主题变量入口：
  - `--app-gradient-primary` / `--app-gradient-primary-hover`
  - `--memo-button-primary-*`

## 2. 次级按钮（Default / Ghost / Danger）

- 典型场景：
  - `打开碎片记录本`
  - `复制 / Markdown / PDF / 删除`
- 统一样式入口：
  - `AppButton` 变体：`default` / `ghost` / `danger` / `link`
  - `.memo-button` / `.memo-button--ghost`
- 主题变量入口：
  - `--app-border-default` `--app-surface-*` `--app-accent-border`
  - `--memo-button-*`

## 3. 文字动作按钮（Link Action）

- 典型场景：
  - 工作台卡片 `进入`
- 统一样式入口：
  - `AppButton variant="link"`
- 主题变量入口：
  - `--app-color-primary`
  - `--app-color-primary-strong`

## 4. 标签 / 状态 Chip

- 典型场景：
  - 智能生成：`列表/表格` 状态、结果状态
  - 碎片记录本：状态标签、日期标签
  - 历史周报：风格标签、`生成周报` 标签
- 统一样式入口：
  - `.memo-chip` + 修饰类：`--accent` `--info` `--success` `--warning` `--danger`
  - 文件：`src/styles/components.css`
- 主题变量入口：
  - `--memo-chip-*`
  - `--app-color-success/warning/danger`

## 5. 分段选择器（列表/表格切换）

- 典型场景：
  - 智能生成和历史周报的 `列表 / 表格`
- 统一样式入口：
  - `.app-segmented` / `.app-segmented__option`
  - 文件：`src/styles/components.css`
- 主题变量入口：
  - `--app-accent-soft`
  - `--app-color-primary`

## 6. 侧边栏导航项（含 hover）

- 典型场景：
  - `收起导航`、菜单项 hover/active
- 统一样式入口：
  - `src/layout/AppSidebar.vue`
- 主题变量入口：
  - `--app-sidebar-hover-bg`
  - `--app-sidebar-active-bg`

## 7. 主题文件总入口

- 默认 Token（基础回退）：`src/styles/tokens.css`
- 紫色主题：`src/styles/theme-light.css`
- 经典蓝主题：`src/styles/theme-light-classic.css`
- Element Plus 主题桥接：`src/assets/main.css`

## 8. 背景与卡片壳层级（新增）

- 统一壳层类（`src/styles/components.css`）：
  - `app-surface--hero`：页面顶层上下文卡（标题栏/主工具栏）
  - `app-surface--panel`：主功能面板卡（列表区、内容区、设置区）
  - `app-surface--inset`：面板内嵌内容卡（详情块、摘要块）
  - `app-surface--subtle`：弱强调区块（提示、次级信息容器）
- 这些类只吃变量，不写死颜色；对应变量在 `tokens.css` 与各 `theme-*.css`：
  - `--app-surface-hero-*`
  - `--app-surface-panel-*`
  - `--app-surface-inset-*`
  - `--app-surface-subtle-*`

## 9. Markdown 与内容展示底色

- 用于历史周报/智能生成结果区的内容底色与表格底色：
  - `--app-markdown-plain-*`
  - `--app-markdown-quote-bg`
  - `--app-markdown-code-bg`
  - `--app-markdown-pre-bg`
  - `--app-markdown-table-*`
- 列表/危险态软背景：
  - `--app-list-item-bg`
  - `--app-list-item-active-bg`
  - `--app-danger-soft-*`

## 10. 说明：哪些情况“不可直接改色”

- 当前你提到的组件都可以改色，且已纳入上述统一入口。
- 没有发现必须“颜色和组件深绑定、完全无法外部主题化”的情况。
