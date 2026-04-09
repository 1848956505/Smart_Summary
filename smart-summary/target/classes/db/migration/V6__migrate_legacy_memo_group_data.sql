-- Migrate legacy memo_group data to memo_folders + memo_week_records.
-- This script is defensive: if legacy table/columns are absent, it becomes a no-op.

CREATE TABLE IF NOT EXISTS `legacy_memo_group_mapping` (
    `legacy_group_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    `new_folder_id` BIGINT NOT NULL,
    `new_week_record_id` BIGINT NULL,
    `migrated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`legacy_group_id`),
    KEY `idx_legacy_memo_group_mapping_user_id` (`user_id`),
    KEY `idx_legacy_memo_group_mapping_new_folder_id` (`new_folder_id`),
    KEY `idx_legacy_memo_group_mapping_new_week_record_id` (`new_week_record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET @has_memo_group := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_group'
);

SET @has_group_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_group'
      AND COLUMN_NAME = 'id'
);

SET @has_group_user_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_group'
      AND COLUMN_NAME = 'user_id'
);

SET @can_migrate_groups := IF(@has_memo_group > 0 AND @has_group_id > 0 AND @has_group_user_id > 0, 1, 0);

SET @has_group_folder_name := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'folder_name'
);
SET @has_group_name := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'name'
);
SET @has_group_title := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'title'
);
SET @has_group_week_start_date := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'week_start_date'
);
SET @has_group_week_end_date := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'week_end_date'
);
SET @has_group_week_date := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'week_date'
);
SET @has_group_create_time := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'create_time'
);
SET @has_group_update_time := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'update_time'
);
SET @has_group_deleted := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'deleted'
);
SET @has_group_deleted_at := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'deleted_at'
);
SET @has_group_sort_order := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group' AND COLUMN_NAME = 'sort_order'
);

SET @expr_group_folder_name := IF(
    @has_group_folder_name = 1,
    "NULLIF(g.folder_name, '')",
    IF(@has_group_name = 1, "NULLIF(g.name, '')", "'默认文件夹'")
);

SET @expr_group_title := IF(
    @has_group_title = 1,
    "NULLIF(g.title, '')",
    IF(@has_group_week_date = 1, "NULLIF(g.week_date, '')", "NULL")
);

SET @expr_group_created_at := IF(
    @has_group_create_time = 1,
    "COALESCE(g.create_time, NOW())",
    "NOW()"
);

SET @expr_group_updated_at := IF(
    @has_group_update_time = 1,
    CONCAT("COALESCE(g.update_time, ", @expr_group_created_at, ")"),
    @expr_group_created_at
);

SET @expr_group_deleted_mark_time := IF(
    @has_group_update_time = 1 AND @has_group_create_time = 1,
    "COALESCE(g.update_time, g.create_time, NOW())",
    IF(
        @has_group_update_time = 1,
        "COALESCE(g.update_time, NOW())",
        IF(@has_group_create_time = 1, "COALESCE(g.create_time, NOW())", "NOW()")
    )
);

SET @expr_group_week_start := IF(
    @has_group_week_start_date = 1,
    "g.week_start_date",
    IF(@has_group_week_date = 1, "STR_TO_DATE(SUBSTRING_INDEX(g.week_date, '~', 1), '%Y-%m-%d')", CONCAT("DATE(", @expr_group_created_at, ")"))
);

SET @expr_group_week_end := IF(
    @has_group_week_end_date = 1,
    "g.week_end_date",
    IF(@has_group_week_date = 1, "STR_TO_DATE(SUBSTRING_INDEX(g.week_date, '~', -1), '%Y-%m-%d')", CONCAT("DATE_ADD(", @expr_group_week_start, ", INTERVAL 6 DAY)"))
);

SET @expr_group_deleted_at := IF(
    @has_group_deleted_at = 1,
    "g.deleted_at",
    IF(@has_group_deleted = 1, CONCAT("IF(IFNULL(g.deleted, 0) = 1, ", @expr_group_deleted_mark_time, ", NULL)"), "NULL")
);

SET @expr_group_filter := IF(
    @has_group_deleted_at = 1,
    "g.deleted_at IS NULL",
    IF(@has_group_deleted = 1, "IFNULL(g.deleted, 0) = 0", "1 = 1")
);

SET @expr_group_sort_order := IF(@has_group_sort_order = 1, "IFNULL(g.sort_order, 0)", "0");

DROP TEMPORARY TABLE IF EXISTS `tmp_legacy_memo_groups`;
CREATE TEMPORARY TABLE `tmp_legacy_memo_groups` (
    `legacy_group_id` BIGINT NOT NULL,
    `user_id` BIGINT NOT NULL,
    `folder_name` VARCHAR(255) NOT NULL,
    `title` VARCHAR(255) NULL,
    `week_start_date` DATE NOT NULL,
    `week_end_date` DATE NOT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    `deleted_at` DATETIME NULL,
    `sort_order` INT NOT NULL DEFAULT 0,
    PRIMARY KEY (`legacy_group_id`),
    KEY `idx_tmp_legacy_memo_groups_user_id` (`user_id`)
) ENGINE=InnoDB;

SET @insert_groups_sql := IF(
    @can_migrate_groups = 1,
    CONCAT(
        "INSERT INTO tmp_legacy_memo_groups (legacy_group_id, user_id, folder_name, title, week_start_date, week_end_date, created_at, updated_at, deleted_at, sort_order) ",
        "SELECT ",
        "g.id AS legacy_group_id, ",
        "g.user_id AS user_id, ",
        "COALESCE(", @expr_group_folder_name, ", '默认文件夹') AS folder_name, ",
        "COALESCE(", @expr_group_title, ", '') AS title, ",
        "COALESCE(", @expr_group_week_start, ", DATE(", @expr_group_created_at, ")) AS week_start_date, ",
        "COALESCE(", @expr_group_week_end, ", DATE_ADD(COALESCE(", @expr_group_week_start, ", DATE(", @expr_group_created_at, ")), INTERVAL 6 DAY)) AS week_end_date, ",
        @expr_group_created_at, " AS created_at, ",
        @expr_group_updated_at, " AS updated_at, ",
        @expr_group_deleted_at, " AS deleted_at, ",
        @expr_group_sort_order, " AS sort_order ",
        "FROM memo_group g ",
        "WHERE ", @expr_group_filter
    ),
    "SELECT 'skip V6: memo_group or required columns not found'"
);

PREPARE stmt_insert_groups FROM @insert_groups_sql;
EXECUTE stmt_insert_groups;
DEALLOCATE PREPARE stmt_insert_groups;

SET @insert_default_folders_sql := IF(
    @can_migrate_groups = 1,
    "INSERT INTO memo_folders (user_id, name, sort_order, is_collapsed, created_at, updated_at, deleted_at)
     SELECT src.user_id, src.folder_name, 0, 0, src.created_at, src.updated_at, NULL
     FROM (
         SELECT user_id,
                COALESCE(NULLIF(folder_name, ''), '默认文件夹') AS folder_name,
                MIN(created_at) AS created_at,
                MAX(updated_at) AS updated_at
         FROM tmp_legacy_memo_groups
         GROUP BY user_id, COALESCE(NULLIF(folder_name, ''), '默认文件夹')
     ) src
     LEFT JOIN memo_folders f
       ON f.user_id = src.user_id
      AND f.name = src.folder_name
      AND f.deleted_at IS NULL
     WHERE f.id IS NULL",
    "SELECT 'skip V6 folder migration'"
);

PREPARE stmt_insert_default_folders FROM @insert_default_folders_sql;
EXECUTE stmt_insert_default_folders;
DEALLOCATE PREPARE stmt_insert_default_folders;

SET @insert_week_records_sql := IF(
    @can_migrate_groups = 1,
    "INSERT INTO memo_week_records (user_id, folder_id, title, week_start_date, week_end_date, status, summary_content, version, created_at, updated_at, deleted_at)
     SELECT
         g.user_id,
         f.id AS folder_id,
         COALESCE(NULLIF(g.title, ''), CONCAT(DATE_FORMAT(g.week_start_date, '%Y-%m-%d'), '~', DATE_FORMAT(g.week_end_date, '%Y-%m-%d'), ' 工作记录')) AS title,
         g.week_start_date,
         g.week_end_date,
         'draft' AS status,
         NULL AS summary_content,
         0 AS version,
         g.created_at,
         g.updated_at,
         g.deleted_at
     FROM tmp_legacy_memo_groups g
     JOIN memo_folders f
       ON f.user_id = g.user_id
      AND f.name = COALESCE(NULLIF(g.folder_name, ''), '默认文件夹')
      AND f.deleted_at IS NULL
     LEFT JOIN memo_week_records w
       ON w.user_id = g.user_id
      AND w.folder_id = f.id
      AND w.week_start_date = g.week_start_date
      AND w.week_end_date = g.week_end_date
      AND w.title = COALESCE(NULLIF(g.title, ''), CONCAT(DATE_FORMAT(g.week_start_date, '%Y-%m-%d'), '~', DATE_FORMAT(g.week_end_date, '%Y-%m-%d'), ' 工作记录'))
      AND (w.deleted_at <=> g.deleted_at)
     WHERE w.id IS NULL
     ORDER BY g.sort_order ASC, g.created_at ASC, g.legacy_group_id ASC",
    "SELECT 'skip V6 week record migration'"
);

PREPARE stmt_insert_week_records FROM @insert_week_records_sql;
EXECUTE stmt_insert_week_records;
DEALLOCATE PREPARE stmt_insert_week_records;

SET @insert_group_mapping_sql := IF(
    @can_migrate_groups = 1,
    "INSERT INTO legacy_memo_group_mapping (legacy_group_id, user_id, new_folder_id, new_week_record_id, migrated_at)
     SELECT
         g.legacy_group_id,
         g.user_id,
         f.id AS new_folder_id,
         (
             SELECT w.id
             FROM memo_week_records w
             WHERE w.user_id = g.user_id
               AND w.folder_id = f.id
               AND w.week_start_date = g.week_start_date
               AND w.week_end_date = g.week_end_date
               AND w.title = COALESCE(NULLIF(g.title, ''), CONCAT(DATE_FORMAT(g.week_start_date, '%Y-%m-%d'), '~', DATE_FORMAT(g.week_end_date, '%Y-%m-%d'), ' 工作记录'))
             ORDER BY w.id DESC
             LIMIT 1
         ) AS new_week_record_id,
         NOW() AS migrated_at
     FROM tmp_legacy_memo_groups g
     JOIN memo_folders f
       ON f.user_id = g.user_id
      AND f.name = COALESCE(NULLIF(g.folder_name, ''), '默认文件夹')
      AND f.deleted_at IS NULL
     ON DUPLICATE KEY UPDATE
         user_id = VALUES(user_id),
         new_folder_id = VALUES(new_folder_id),
         new_week_record_id = VALUES(new_week_record_id),
         migrated_at = VALUES(migrated_at)",
    "SELECT 'skip V6 mapping table update'"
);

PREPARE stmt_insert_group_mapping FROM @insert_group_mapping_sql;
EXECUTE stmt_insert_group_mapping;
DEALLOCATE PREPARE stmt_insert_group_mapping;
