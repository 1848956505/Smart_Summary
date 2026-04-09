# SmartSummary Pro

SmartSummary Pro is a work-summary assistant with a Vue 3 front end and a Spring Boot back end.

## What Changed Recently

- The memo module has been refactored from the legacy `memo_group` / `memo_fragment` model to:
  - `memo_folders`
  - `memo_week_records`
  - `memo_fragments`
- Weekly summaries now trace back to the source week record.
- The front end was refactored into a formal enterprise workspace layout with centralized theme tokens and reusable UI primitives.
- The memo workspace keeps its three-column workflow but now follows the same enterprise panel system as the rest of the app.
- The project now uses a single unified launcher: `start.bat`.

## Tech Stack

- Back end: Spring Boot 3, MyBatis-Plus, Flyway, MySQL
- Front end: Vue 3, Vite, Element Plus, Tailwind CSS
- AI integration: LLM summary generation service

## Project Structure

```text
smart-summary/              Back-end Spring Boot app
smart-summary-web/          Front-end Vue app
README.md                   Project overview and usage
start.bat                   Unified launcher for local development
start-dev-auto-port.ps1     Helper script used by the launcher
```

## Main Features

- User login and registration
- Work summary generation
- History browsing, copy, and export
- Dashboard workspace with quick actions and recent activity
- Memo workspace with:
  - folder tree
  - week records
  - daily fragments
  - weekly summary generation and saving
  - source traceability for historical summaries
- Settings page for user and model configuration

## Local Development

### 1. Start the whole project

Use the single launcher from the repository root:

```powershell
start.bat
```

The launcher will:

- detect free ports automatically
- start the back end
- start the front end
- wire the front-end proxy to the selected back-end port

### 2. Back-end only

```powershell
cd smart-summary
mvn spring-boot:run
```

### 3. Front-end only

```powershell
cd smart-summary-web
npm install
npm run dev
```

## Memo Refactor Notes

The memo workspace now uses the new structure below:

- folder tree on the left
- week records under each folder
- daily fragments in the center panel
- weekly summary and statistics on the right

Editing flows now use in-app dialogs instead of browser popups and follow the shared enterprise panel style.

## Front-End Architecture

The front end now follows a layered structure:

- `src/layout` for the application shell
- `src/pages` for route pages
- `src/components/ui` for reusable UI primitives
- `src/services` for API access
- `src/styles` for design tokens and theme rules
- `src/constants` for navigation and UI constants

Primary route pages:

- `smart-summary-web/src/pages/dashboard/DashboardPage.vue`
- `smart-summary-web/src/pages/generate/GeneratePage.vue`
- `smart-summary-web/src/pages/history/HistoryPage.vue`
- `smart-summary-web/src/pages/memos/MemosPage.vue`
- `smart-summary-web/src/pages/settings/SettingsPage.vue`

## Database Notes

Flyway migrations are used for schema changes and legacy data migration.

Key tables:

- `memo_folders`
- `memo_week_records`
- `memo_fragments`
- `summary_records`

Legacy tables are archived and should no longer be used for new development.

## Conventions

- Front-end memo requests rely on the logged-in user context.
- Memo queries should always respect user ownership and soft-delete filters.
- New features should follow the modern memo model, not the legacy `memo_group` semantics.

## Ports

- Front end: auto-selected by the launcher, usually in the `3000-3010` range
- Back end: auto-selected by the launcher, usually in the `8080-8090` range

## Notes

If you need to change UI behavior or memo flows, check the following areas first:

- `smart-summary-web/src/layout/*`
- `smart-summary-web/src/pages/*`
- `smart-summary-web/src/components/ui/*`
- `smart-summary-web/src/components/memo/*`
- `smart-summary-web/src/styles/*`

If you need to change database behavior, start with the Flyway migration scripts under:

- `smart-summary/src/main/resources/db/migration`
