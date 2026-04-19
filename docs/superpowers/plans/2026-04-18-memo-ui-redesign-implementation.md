# Memo UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the Smart Summary shell and memo workspace into the approved flagship efficiency workspace without changing memo business logic.

**Architecture:** Establish global shell primitives first so the redesign has a reusable foundation, then refactor the memo workspace in layers: layout shell, left reference rail, top context bar, daily timeline, and quick capture. Finish with a responsive polish pass and verification so the memo page can serve as the model for later page redesigns.

**Tech Stack:** Vue 3, Vue Router, Element Plus, Vite, scoped CSS, app-wide CSS tokens/themes

---

## File Structure Map

### Global shell and visual foundation

- Modify: `smart-summary-web/src/styles/tokens.css`
  - Extend design tokens for warm neutrals, shell spacing, width modes, and refined shadows/radii.
- Modify: `smart-summary-web/src/styles/theme-light.css`
  - Apply the new warm branded surface/background variables.
- Modify: `smart-summary-web/src/styles/components.css`
  - Update shared surface and page-shell primitives to match soft layering.
- Modify: `smart-summary-web/src/layout/AppLayout.vue`
  - Control mixed-width page behavior and shell spacing.
- Modify: `smart-summary-web/src/layout/AppContent.vue`
  - Host content width modes and shell background behavior.
- Modify: `smart-summary-web/src/layout/AppSidebar.vue`
  - Redesign the global flagship product sidebar.
- Modify: `smart-summary-web/src/router/index.js`
  - Tag routes with standard or workspace width mode metadata.

### Memo workspace page and components

- Modify: `smart-summary-web/src/views/MemosView.vue`
  - Rebuild the memo page structure into reference rail, context bar, main timeline stage, and bottom quick capture zone.
- Modify: `smart-summary-web/src/components/memo/MemoSidebar.vue`
  - Rework the semi-immersive reference rail visuals and hierarchy.
- Modify: `smart-summary-web/src/components/memo/WeekRecordHeader.vue`
  - Replace the current large card feel with a restrained week context bar.
- Modify: `smart-summary-web/src/components/memo/DailyFragmentList.vue`
  - Elevate the timeline into chapter-based day sections with refined date anchors.
- Modify: `smart-summary-web/src/components/memo/FragmentCard.vue`
  - Restyle fragments as content-first entries with quieter action handling.
- Modify: `smart-summary-web/src/components/memo/MemoQuickComposer.vue`
  - Convert the composer into a lightweight bottom quick capture bar.

### Verification

- Use existing verification command: `npm run build`
- Manual QA in browser for memo workspace and at least one standard-width page plus one workspace-width page

## Task 1: Establish Global Design Tokens and Width Modes

**Files:**
- Modify: `smart-summary-web/src/styles/tokens.css`
- Modify: `smart-summary-web/src/styles/theme-light.css`
- Modify: `smart-summary-web/src/styles/components.css`

- [ ] **Step 1: Add the new global token groups**

Add shell/layout tokens that support the approved mixed-width and warm branded design language.

```css
:root {
  --app-shell-gutter: 20px;
  --app-shell-gutter-wide: 28px;
  --app-content-max-standard: 1120px;
  --app-content-max-workspace: 1480px;
  --app-color-bg-base: #f5f1eb;
  --app-color-bg-shell: #f7f4ef;
  --app-color-bg-panel: rgba(255, 252, 247, 0.88);
  --app-color-border-soft: rgba(110, 99, 87, 0.12);
  --app-shadow-shell: 0 18px 48px rgba(50, 38, 28, 0.08);
}
```

- [ ] **Step 2: Add refined theme variables for the light theme**

Map the new tone into reusable panel and page variables.

```css
:root,
.theme-light {
  --app-page-bg: linear-gradient(180deg, #f8f5f0 0%, #f2ede7 100%);
  --app-panel-bg: rgba(255, 252, 247, 0.86);
  --app-panel-bg-soft: rgba(250, 246, 240, 0.92);
  --app-panel-border: rgba(110, 99, 87, 0.12);
  --app-panel-shadow: 0 16px 40px rgba(50, 38, 28, 0.08);
}
```

- [ ] **Step 3: Add shared page-shell width helpers**

Define shared utility classes or base selectors for standard and workspace content widths.

```css
.app-page-width--standard {
  width: min(100%, var(--app-content-max-standard));
  margin: 0 auto;
}

.app-page-width--workspace {
  width: min(100%, var(--app-content-max-workspace));
  margin: 0 auto;
}
```

- [ ] **Step 4: Run build to catch CSS regressions**

Run: `npm run build`

Expected: Vite build succeeds with no syntax errors.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/styles/tokens.css smart-summary-web/src/styles/theme-light.css smart-summary-web/src/styles/components.css
git commit -m "feat: add redesigned shell tokens"
```

## Task 2: Rebuild the Global Shell for Mixed-Width Pages

**Files:**
- Modify: `smart-summary-web/src/layout/AppLayout.vue`
- Modify: `smart-summary-web/src/layout/AppContent.vue`
- Modify: `smart-summary-web/src/layout/AppSidebar.vue`
- Modify: `smart-summary-web/src/router/index.js`

- [ ] **Step 1: Add route-level width metadata**

Annotate routes so standard pages and workspace pages can share one shell.

```js
{ path: 'dashboard', name: 'Dashboard', component: DashboardPage, meta: { contentWidth: 'standard' } },
{ path: 'generate', name: 'Generate', component: GeneratePage, meta: { contentWidth: 'workspace', fullBleed: true } },
{ path: 'memos', name: 'Memos', component: MemosPage, meta: { contentWidth: 'workspace' } },
{ path: 'history', name: 'History', component: HistoryPage, meta: { contentWidth: 'workspace' } },
{ path: 'settings', name: 'SettingsPage', component: SettingsPage, meta: { contentWidth: 'standard' } }
```

- [ ] **Step 2: Pass width mode through the shell**

Update layout/content components so route metadata drives shell spacing and content width classes.

```vue
<AppContent :full-bleed="isFullBleed" :content-width="contentWidth">
  <router-view />
</AppContent>
```

```js
const contentWidth = computed(() => route.meta?.contentWidth || 'standard')
```

- [ ] **Step 3: Redesign the global sidebar as the flagship shell rail**

Keep current behavior, but move the visuals away from admin-card styling and toward a calmer flagship product sidebar.

```css
.app-sidebar {
  background: rgba(255, 251, 245, 0.72);
  border: 1px solid var(--app-panel-border);
  box-shadow: none;
  backdrop-filter: blur(18px);
}

.app-sidebar__item--active {
  background: rgba(196, 160, 107, 0.12);
  color: var(--app-color-text-strong);
}
```

- [ ] **Step 4: Run build to verify shell integration**

Run: `npm run build`

Expected: PASS, with the route metadata and layout components compiling correctly.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/layout/AppLayout.vue smart-summary-web/src/layout/AppContent.vue smart-summary-web/src/layout/AppSidebar.vue smart-summary-web/src/router/index.js
git commit -m "feat: add flagship shell width system"
```

## Task 3: Rebuild the Memo Workspace Frame

**Files:**
- Modify: `smart-summary-web/src/views/MemosView.vue`
- Modify: `smart-summary-web/src/pages/memos/MemosPage.vue`

- [ ] **Step 1: Restructure the memo page DOM into the approved frame**

Reshape the page into four visible zones: left reference rail, top context bar, main timeline stage, bottom quick capture.

```vue
<div class="memo-workspace">
  <MemoSidebar ... />

  <section class="memo-workspace__main">
    <WeekRecordHeader ... />
    <div class="memo-workspace__stage">
      <div class="memo-workspace__filters">...</div>
      <div class="memo-workspace__timeline-shell">
        <DailyFragmentList ... />
      </div>
    </div>
    <MemoQuickComposer ... />
  </section>
</div>
```

- [ ] **Step 2: Add main shell spacing and anchoring styles**

Replace the current negative-margin shell with explicit workspace spacing so the page reads as a unified stage.

```css
.memo-workspace {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 24px;
  min-height: 100%;
}

.memo-workspace__main {
  min-width: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 18px;
}
```

- [ ] **Step 3: Keep MemosPage as a thin wrapper**

Do not add logic to `MemosPage.vue`; keep it as a route wrapper so all memo UI work remains inside `MemosView.vue`.

```vue
<template>
  <MemosView />
</template>
```

- [ ] **Step 4: Run build to verify memo frame compilation**

Run: `npm run build`

Expected: PASS with no Vue template or scoped CSS errors.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/views/MemosView.vue smart-summary-web/src/pages/memos/MemosPage.vue
git commit -m "feat: restructure memo workspace frame"
```

## Task 4: Redesign the Memo Reference Rail

**Files:**
- Modify: `smart-summary-web/src/components/memo/MemoSidebar.vue`

- [ ] **Step 1: Reduce visual noise in the sidebar header and footer**

Turn the current large brand/control treatment into a quiet reference rail header.

```css
.memo-sidebar__top {
  align-items: center;
}

.memo-sidebar__eyebrow {
  color: rgba(92, 80, 67, 0.58);
  letter-spacing: 0.14em;
}
```

- [ ] **Step 2: Restyle folder and week rows into refined navigation entries**

Use lighter layering, gentler selected states, and better text rhythm.

```css
.folder-block {
  background: transparent;
  border: 0;
}

.week-row.selected {
  background: rgba(255, 249, 241, 0.96);
  border-color: rgba(183, 146, 92, 0.24);
  box-shadow: 0 10px 22px rgba(72, 52, 31, 0.06);
}
```

- [ ] **Step 3: Compress low-frequency actions**

Move rename/delete affordances toward overflow emphasis rather than equal button prominence.

```vue
<el-dropdown trigger="click">
  <button class="memo-sidebar__more">•••</button>
  <template #dropdown>...</template>
</el-dropdown>
```

- [ ] **Step 4: Run build and manually inspect the rail**

Run: `npm run build`

Expected: PASS. In browser, the left rail should feel calmer and visually secondary to the main stage.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/components/memo/MemoSidebar.vue
git commit -m "feat: redesign memo reference rail"
```

## Task 5: Convert the Week Header into a Context Bar

**Files:**
- Modify: `smart-summary-web/src/components/memo/WeekRecordHeader.vue`

- [ ] **Step 1: Simplify the markup into context groups**

Keep the same data, but reorganize into title/date block, metadata row, and actions group.

```vue
<section class="week-header">
  <div class="week-header__identity">...</div>
  <div class="week-header__meta">...</div>
  <div class="week-header__actions">...</div>
</section>
```

- [ ] **Step 2: Promote only the primary action**

Make "generate weekly summary" the only visually dominant action. Push export/save/copy into secondary or tertiary presentation.

```vue
<el-button class="week-header__primary" type="primary" :loading="generating">
  一键生成周报
</el-button>
```

- [ ] **Step 3: Restyle the header away from a dashboard card**

Use lower height, flatter information rhythm, and lighter metrics.

```css
.week-header {
  padding: 18px 22px;
  background: rgba(255, 251, 245, 0.72);
  border: 1px solid var(--app-panel-border);
}

.week-header__meta {
  font-size: 12px;
  color: var(--app-color-text-muted);
}
```

- [ ] **Step 4: Run build and inspect action hierarchy**

Run: `npm run build`

Expected: PASS. In browser, the header should read as context, not a hero card.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/components/memo/WeekRecordHeader.vue
git commit -m "feat: turn memo header into context bar"
```

## Task 6: Elevate the Daily Timeline into the Main Stage

**Files:**
- Modify: `smart-summary-web/src/components/memo/DailyFragmentList.vue`

- [ ] **Step 1: Refine day-section markup for chapter-like presentation**

Keep the current loop and behavior, but organize the date anchor, heading, and summary into a cleaner chapter header.

```vue
<div class="daily-section__anchor">...</div>
<div class="daily-section__heading">...</div>
<div class="daily-section__summary">...</div>
```

- [ ] **Step 2: Soften the timeline rails and anchors**

Preserve the calendar timeline concept, but reduce the admin feel and improve editorial rhythm.

```css
.daily-list::before {
  background: linear-gradient(to bottom, transparent, rgba(173, 156, 138, 0.32) 12%, rgba(173, 156, 138, 0.32) 88%, transparent);
}

.daily-section__calendar {
  background: rgba(255, 252, 247, 0.94);
  border-color: rgba(110, 99, 87, 0.1);
}
```

- [ ] **Step 3: Make the day body feel like a refined content column**

Increase reading quality and chapter separation without turning each day into an oversized card.

```css
.daily-section {
  padding: 8px 0 18px;
}

.daily-section__body {
  gap: 14px;
}
```

- [ ] **Step 4: Run build and visually inspect the timeline**

Run: `npm run build`

Expected: PASS. In browser, day sections should read as the primary visual structure.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/components/memo/DailyFragmentList.vue
git commit -m "feat: elevate memo daily timeline"
```

## Task 7: Redesign Fragment Cards as Content Entries

**Files:**
- Modify: `smart-summary-web/src/components/memo/FragmentCard.vue`

- [ ] **Step 1: Reduce card heaviness and emphasize content rhythm**

Keep metadata, title, text, and actions, but make the layout feel more like a content object than a module.

```css
.fragment-card {
  padding: 18px 20px;
  background: rgba(255, 253, 250, 0.96);
  border: 1px solid rgba(110, 99, 87, 0.08);
  box-shadow: 0 10px 24px rgba(53, 37, 24, 0.05);
}
```

- [ ] **Step 2: Quiet the action cluster until hover/focus**

Keep edit, reorder, and delete available, but reduce their default prominence.

```css
.fragment-card__actions {
  opacity: 0.38;
}

.fragment-card:hover .fragment-card__actions,
.fragment-card:focus-within .fragment-card__actions {
  opacity: 1;
}
```

- [ ] **Step 3: Tighten metadata styling**

Make tags and dates supportive rather than equal-weight UI chips everywhere.

```css
.fragment-card__date {
  font-size: 11px;
  letter-spacing: 0.02em;
}
```

- [ ] **Step 4: Run build and inspect at desktop and mobile widths**

Run: `npm run build`

Expected: PASS. In browser, cards should feel calmer and more editorial without hiding actions.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/components/memo/FragmentCard.vue
git commit -m "feat: redesign memo fragment cards"
```

## Task 8: Rebuild the Quick Capture Bar

**Files:**
- Modify: `smart-summary-web/src/components/memo/MemoQuickComposer.vue`

- [ ] **Step 1: Keep behavior but shift the visual model**

Do not change the submit/update/open-detail behavior. Change the component to read as a lightweight capture bar fixed to the bottom of the main workspace.

```vue
<section class="memo-composer">
  <div class="memo-composer__context">...</div>
  <div class="memo-composer__field">...</div>
  <div class="memo-composer__meta">...</div>
</section>
```

- [ ] **Step 2: Add calm default state and stronger focus state**

Use soft transparency and blur sparingly so the composer feels premium but not loud.

```css
.memo-composer {
  background: rgba(255, 250, 244, 0.82);
  border: 1px solid rgba(110, 99, 87, 0.1);
  backdrop-filter: blur(16px);
}

.memo-composer:focus-within {
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 18px 38px rgba(54, 38, 25, 0.1);
}
```

- [ ] **Step 3: Keep the primary action explicit and the detail route quiet**

The submit affordance should stay obvious; the detailed-entry action should read as secondary support.

```css
.memo-composer__footer-link {
  color: var(--app-color-text-soft);
}
```

- [ ] **Step 4: Run build and manually test composer interaction**

Run: `npm run build`

Expected: PASS. In browser, the composer should feel light when idle and clearly active on focus.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/components/memo/MemoQuickComposer.vue
git commit -m "feat: redesign memo quick capture bar"
```

## Task 9: Integrate Workspace Polish and Responsive Behavior

**Files:**
- Modify: `smart-summary-web/src/views/MemosView.vue`
- Modify: `smart-summary-web/src/components/memo/MemoSidebar.vue`
- Modify: `smart-summary-web/src/components/memo/WeekRecordHeader.vue`
- Modify: `smart-summary-web/src/components/memo/DailyFragmentList.vue`
- Modify: `smart-summary-web/src/components/memo/FragmentCard.vue`
- Modify: `smart-summary-web/src/components/memo/MemoQuickComposer.vue`

- [ ] **Step 1: Tune spacing, breakpoints, and sticky behavior**

Make the page feel intentional across desktop and smaller screens.

```css
@media (max-width: 1280px) {
  .memo-workspace {
    grid-template-columns: 1fr;
  }
}
```

- [ ] **Step 2: Ensure main-stage priority survives on narrower widths**

On smaller screens, keep the timeline first in importance and avoid letting filters or controls crowd it.

```css
@media (max-width: 860px) {
  .memo-workspace__filters {
    order: 2;
  }
}
```

- [ ] **Step 3: Verify no component still looks like the old admin-card language**

Audit the memo page against the design spec:

- left rail should feel quiet
- top bar should feel contextual
- timeline should feel primary
- quick capture should feel light but ready

- [ ] **Step 4: Run build for integrated pass**

Run: `npm run build`

Expected: PASS with the integrated memo workspace redesign complete.

- [ ] **Step 5: Commit**

```bash
git add smart-summary-web/src/views/MemosView.vue smart-summary-web/src/components/memo/MemoSidebar.vue smart-summary-web/src/components/memo/WeekRecordHeader.vue smart-summary-web/src/components/memo/DailyFragmentList.vue smart-summary-web/src/components/memo/FragmentCard.vue smart-summary-web/src/components/memo/MemoQuickComposer.vue
git commit -m "feat: polish memo workspace redesign"
```

## Task 10: Final Verification and Handoff

**Files:**
- Modify if needed: `docs/superpowers/specs/2026-04-18-memo-ui-redesign-design.md`
- No code change expected unless verification uncovers issues

- [ ] **Step 1: Run final build verification**

Run: `npm run build`

Expected: PASS

- [ ] **Step 2: Perform manual browser QA**

Check:

- memo workspace route
- one standard-width page such as settings
- one workspace-width page such as history or generate

Expected:

- mixed-width shell works
- sidebar feels consistent
- memo page matches the approved hierarchy

- [ ] **Step 3: Record any spec mismatches and fix before handoff**

If the build passes but the UI violates the approved spec, fix the UI before declaring completion.

- [ ] **Step 4: Prepare change summary**

Summarize:

- what changed in global shell
- what changed in memo workspace
- what remains for later page redesigns

- [ ] **Step 5: Commit final verification fixes if needed**

```bash
git add smart-summary-web
git commit -m "chore: finalize memo redesign verification"
```

## Spec Coverage Check

This plan covers the approved spec sections as follows:

- Global shell direction: Tasks 1-2
- Memo workspace layout restructuring: Tasks 3-5
- Memo timeline as primary stage: Tasks 6-7
- Quick capture redesign: Task 8
- Responsive and verification checkpoints: Tasks 9-10
- Future reuse for other pages: Tasks 1-2 and Task 10 handoff

No approved spec section is intentionally left without a corresponding task.

## Placeholder Scan

The plan avoids "TBD", "TODO", or deferred implementation markers. Each task names exact files, gives a concrete intent, and includes explicit verification commands.

## Type Consistency Check

The plan preserves current component and route names:

- `AppLayout`
- `AppContent`
- `AppSidebar`
- `MemosView`
- `MemoSidebar`
- `WeekRecordHeader`
- `DailyFragmentList`
- `FragmentCard`
- `MemoQuickComposer`

It also preserves the route metadata naming introduced in the plan as `contentWidth`, used consistently in shell tasks.
