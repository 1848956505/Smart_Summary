# Memo/Sidebar 展开收缩动画实现参考

## 目标
- 收缩时视觉稳定，不抖动、不闪烁。
- 图标位置可预期，文本平滑淡出。
- 动画只影响布局和透明度，避免重排抖动。

## 核心做法
1. 容器宽度动画
- 对侧栏根容器同时过渡 `width` 与 `min-width`。
- 推荐时长：`0.25s`，缓动：`ease`。
- 示例：
```css
transition: width 0.25s ease, min-width 0.25s ease;
will-change: width, min-width;
```

2. 内层留白同步动画
- 对内层壳容器的 `padding` 做同速过渡，避免“宽度变了但内边距瞬移”。
- 示例：
```css
transition: padding 0.25s ease;
```

3. 文本分层淡出而非 `display: none`
- 品牌文案、导航文案、按钮文案、用户信息统一采用：
  - `max-width` 从正常值过渡到 `0`
  - `opacity` 过渡到 `0`
  - `transform: translateX(-8px)` 轻微位移
- 避免直接 `display: none` 导致闪断。

4. 图标锚点固定
- 展开态：`justify-content: flex-start`
- 收缩态：`justify-content: center`（或设计要求的 `flex-end`）
- 保证图标在动画中有稳定锚点，减少“漂移感”。

5. 收缩态操作位去重
- 同一行为只保留一个入口（例如“展开”只留一个方形按钮）。
- 减少重复按钮带来的交互歧义和视觉噪音。

## 本项目落地位置
- 碎片记录本侧栏：`smart-summary-web/src/components/memo/MemoSidebar.vue`
  - 收缩态只保留右上角方形展开按钮
  - 底部“新建文件夹”按钮保留并在收缩态切换为渐变主按钮

- 主侧栏：`smart-summary-web/src/layout/AppSidebar.vue`
  - 宽度与内边距过渡统一为 `0.25s ease`
  - 文案区域过渡时长统一为 `0.25s`
  - 保持与碎片记录本侧栏同款节奏

## 调参建议
- 若想更“利落”：时长降到 `0.22s`
- 若想更“柔和”：时长升到 `0.28s`
- 不建议超过 `0.32s`，会明显拖慢交互反馈

