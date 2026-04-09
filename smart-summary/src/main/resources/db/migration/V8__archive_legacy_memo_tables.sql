-- Archive legacy memo tables after memo_refactor stabilization.
-- This script is idempotent and safe to run repeatedly.

SET @has_memo_group := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group'
);
SET @has_memo_group_legacy := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group_legacy'
);
SET @rename_memo_group_sql := IF(
    @has_memo_group = 1 AND @has_memo_group_legacy = 0,
    'RENAME TABLE `memo_group` TO `memo_group_legacy`',
    'SELECT ''skip memo_group archive'''
);
PREPARE stmt_rename_memo_group FROM @rename_memo_group_sql;
EXECUTE stmt_rename_memo_group;
DEALLOCATE PREPARE stmt_rename_memo_group;

SET @has_memo_fragment := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment'
);
SET @has_memo_fragment_legacy := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment_legacy'
);
SET @rename_memo_fragment_sql := IF(
    @has_memo_fragment = 1 AND @has_memo_fragment_legacy = 0,
    'RENAME TABLE `memo_fragment` TO `memo_fragment_legacy`',
    'SELECT ''skip memo_fragment archive'''
);
PREPARE stmt_rename_memo_fragment FROM @rename_memo_fragment_sql;
EXECUTE stmt_rename_memo_fragment;
DEALLOCATE PREPARE stmt_rename_memo_fragment;
