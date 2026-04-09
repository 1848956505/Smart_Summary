SET @source_col_exists := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'summary_records'
      AND COLUMN_NAME = 'source_week_record_id'
);

SET @add_source_col_sql := IF(
    @source_col_exists = 0,
    'ALTER TABLE `summary_records` ADD COLUMN `source_week_record_id` BIGINT NULL AFTER `user_id`',
    'SELECT 1'
);

PREPARE stmt_add_col FROM @add_source_col_sql;
EXECUTE stmt_add_col;
DEALLOCATE PREPARE stmt_add_col;

SET @source_idx_exists := (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'summary_records'
      AND INDEX_NAME = 'idx_summary_records_source_week_record_id'
);

SET @add_source_idx_sql := IF(
    @source_idx_exists = 0,
    'CREATE INDEX `idx_summary_records_source_week_record_id` ON `summary_records` (`source_week_record_id`)',
    'SELECT 1'
);

PREPARE stmt_add_idx FROM @add_source_idx_sql;
EXECUTE stmt_add_idx;
DEALLOCATE PREPARE stmt_add_idx;
