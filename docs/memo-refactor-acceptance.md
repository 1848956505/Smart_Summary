# Memo Refactor Acceptance Checklist

## 1. Data Layer Acceptance

### 1.1 New table creation
- [ ] `memo_folders` table exists with required fields and indexes.
- [ ] `memo_week_records` table exists with required fields, indexes, and `folder_id` foreign key.
- [ ] `memo_fragments` table exists with required fields and indexes.
- [ ] `summary_records.source_week_record_id` field and index exist.

### 1.2 Legacy data migration
- [ ] `V6__migrate_legacy_memo_group_data.sql` executed successfully.
- [ ] `V7__migrate_legacy_memo_fragment_data.sql` executed successfully.
- [ ] Default folder creation logic worked for users without explicit folder semantics.

### 1.3 Count reconciliation
- [ ] Old `memo_group` count matches migrated `memo_week_records` count expectation.
- [ ] Old `memo_fragment` count matches migrated `memo_fragments` count expectation.
- [ ] Per-user record counts are consistent before and after migration.
- [ ] No rows with missing `folder_id` in `memo_week_records`.
- [ ] No rows with missing `week_record_id` in `memo_fragments`.

## 2. Backend Acceptance

### 2.1 API behavior
- [ ] `GET/POST/PUT/DELETE /api/memo/folders` returns normal success responses.
- [ ] `GET/POST/PUT/DELETE /api/memo/weeks` returns normal success responses.
- [ ] `GET/POST/PUT/DELETE /api/memo/fragments` returns normal success responses.
- [ ] `POST /api/memo/weeks/{id}/generate-summary` returns summary and stats.
- [ ] `POST /api/memo/weeks/{id}/save-summary` persists summary content.

### 2.2 Ownership and security
- [ ] Current user is resolved from `X-User-Id` login context.
- [ ] API does not trust frontend `userId` payload.
- [ ] Cross-user resource access is rejected.
- [ ] Query/update/delete paths include user ownership validation.

### 2.3 Weekly summary chain
- [ ] Summary generation reads fragments by `week_record_id`.
- [ ] Fragment ordering uses `work_date` + `sort_order`.
- [ ] Generated text is written back to `memo_week_records.summary_content`.
- [ ] `summary_records` upsert links `source_week_record_id`.

### 2.4 Regression tests
- [ ] `MemoControllerRegressionTest` passes.
- [ ] `MemoFragmentServiceOwnershipTest` passes.
- [ ] Test coverage includes folder/week/fragment create-read chain, summary generation, week delete path, and cross-user rejection.

## 3. Frontend Acceptance

### 3.1 Left tree
- [ ] Level-1 nodes are folders (`name`).
- [ ] Level-2 nodes are week records (`weekRecord`).
- [ ] Folder expand/collapse works.
- [ ] Folder CRUD works.
- [ ] Week record CRUD works.
- [ ] Selected folder/week highlight works.

### 3.2 Right panel
- [ ] Right panel binds to `weekRecord` instead of legacy `group`.
- [ ] Header shows title, week range, fragment count.
- [ ] Day-based fragment list renders correctly.
- [ ] Fragment add/edit/delete/reorder works.

### 3.3 Weekly summary UX
- [ ] One-click generation shows summary result.
- [ ] Copy summary works.
- [ ] Save summary to history works.
- [ ] `summary_content` is echoed back after refresh.
- [ ] Last selected week can be restored after page reload.

## 4. Final Joint Validation Flow
- [ ] Create folder -> create week -> add fragments -> generate summary -> save summary -> refresh page -> verify summary recovery.
- [ ] Delete week record -> verify logical deletion and absence from active list.
- [ ] Simulate another user id -> verify access rejection for existing week/fragments.
