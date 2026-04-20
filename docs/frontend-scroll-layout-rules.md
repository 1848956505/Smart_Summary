# 前端滚动布局约定

本文档用于记录 `碎片记录本` 与 `历史周报` 重构过程中反复踩到的滚动布局问题，后续所有“工作台型页面”都应遵守这里的规则。

## 目标

对于这类页面，我们要的不是“浏览器整页滚动”，而是：

- 页面外壳固定
- 顶部工具条固定
- 左侧栏可单独滚动
- 右侧主舞台可单独滚动

## 正确结构

推荐结构：

1. 页面根容器固定高度
2. 页面内部主布局占满剩余高度
3. 真正需要滚动的那一层，必须是唯一的滚动容器

以工作台页面为例：

```css
.page {
  flex: 1;
  min-height: calc(100vh - ...);
  height: calc(100vh - ...);
  overflow: hidden;
}

.page__layout {
  flex: 1;
  min-height: 0;
  height: 0;
  overflow: hidden;
}

.page__panel {
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page__scroll {
  flex: 1 1 0;
  min-height: 0;
  height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}
```

## 必须遵守的规则

### 1. 外层应用壳不能放行页面级滚动

如果目标是“局部滚动”，那么：

- `body` 不应承担页面滚动
- `AppContent` 不应使用 `overflow: visible`
- 内容外壳需要固定高度链

这次的有效写法在：

- [AppContent.vue](/D:/A-Projects/Smart_Summary/smart-summary-web/src/layout/AppContent.vue)
- [base.css](/D:/A-Projects/Smart_Summary/smart-summary-web/src/styles/base.css)

## 2. `min-height: 0` 是关键，不是可选项

只要父层是 `flex` 或 `grid`，子层如果想成为滚动容器，通常都必须补：

- `min-height: 0`
- 必要时再补 `height: 0`

否则它会继续按内容自然撑高，滚动条不会出现在我们希望的那一层。

## 3. 不要把内容块误写成 `flex: 1`

这次历史周报右侧不滚动的直接原因之一，就是：

- “生成周报”块被写成了 `flex: 1`

结果不是文档区滚动，而是内容块自己吃满剩余空间，导致外层滚动容器没有超出内容。

结论：

- 滚动容器用 `flex: 1`
- 内容块默认用自然高度
- 除非非常明确，否则不要给内容块乱加 `flex: 1`

## 4. 一个区域只保留一个主滚动容器

如果同一块区域里：

- 外层能滚
- 中层也能滚
- 内层也能滚

就会出现：

- 滚动行为不稳定
- 鼠标滚轮被错误容器接管
- 某些状态下能滚，切换后又不能滚

最佳实践：

- 明确指定唯一的 `.page__scroll`
- 其它父层统一 `overflow: hidden`

## 5. 对照已验证的工作结构，不要重新发明

后续如果再做工作台页，优先参考这两个已经验证通过的页面：

- [MemosView.vue](/D:/A-Projects/Smart_Summary/smart-summary-web/src/views/MemosView.vue)
- [HistoryPage.vue](/D:/A-Projects/Smart_Summary/smart-summary-web/src/pages/history/HistoryPage.vue)

尤其参考这些层：

- 页面根容器高度
- 布局容器 `height: 0`
- 滚动层 `flex: 1 1 0 + min-height: 0 + height: 0 + overflow-y: auto`

## 排查顺序

以后如果再遇到“应该局部滚动，却变成整页滚动 / 不滚动”，按这个顺序查：

1. `body` 是否还在滚
2. `AppContent` 是否仍然 `overflow: visible`
3. 页面根容器是否有明确高度
4. 主布局层是否有 `min-height: 0` / `height: 0`
5. 面板层是否 `overflow: hidden`
6. 真正滚动层是否同时具备：
   - `flex: 1 1 0`
   - `min-height: 0`
   - `height: 0`
   - `overflow-y: auto`
7. 是否有某个内容块误写成 `flex: 1`

## 后续执行约定

从现在开始，新的工作台型页面在进入样式细化前，先优先完成：

1. 高度链正确
2. 滚动容器唯一
3. 浏览器页面不参与滚动

也就是说：

先把滚动模型做对，再做视觉。
