# Memo Legacy Archive Notes

## 1. Archive target
- Legacy table `memo_group` is archived to `memo_group_legacy`.
- Legacy table `memo_fragment` (old structure) is archived to `memo_fragment_legacy` when present.

## 2. Flyway migration
- Added migration: `src/main/resources/db/migration/V8__archive_legacy_memo_tables.sql`
- Script behavior:
  - Checks table existence from `information_schema.TABLES`.
  - Renames only when source table exists and target legacy table does not exist.
  - Is idempotent for repeated runs.

## 3. Code dependency cleanup status
- Runtime memo chain (`folders -> week records -> fragments`) does not use legacy `memo_group` table.
- Legacy compatibility entity is mapped to `memo_group_legacy` only.
- Legacy repository is intentionally not registered as Spring bean to avoid accidental runtime usage.

## 4. Post-archive verification
- Confirm app startup with Flyway migration to V8 success.
- Confirm all memo APIs still operate on:
  - `memo_folders`
  - `memo_week_records`
  - `memo_fragments`
- Confirm no new feature code references `memo_group` or `memo_fragment` old structure.

## 5. Optional hardening recommendations
- In next cleanup window, fully remove legacy entity/repository source files.
- Restrict direct SQL privileges on `*_legacy` tables to read-only for DBA/admin tooling.
