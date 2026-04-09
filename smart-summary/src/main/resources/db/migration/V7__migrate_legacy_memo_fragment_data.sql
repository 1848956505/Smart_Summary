-- Migrate legacy memo_fragment data to memo_fragments.
-- This script is defensive: if legacy table/columns are absent, it becomes a no-op.

CREATE TABLE IF NOT EXISTS `legacy_memo_fragment_mapping` (
    `legacy_fragment_id` BIGINT NOT NULL,
    `legacy_group_id` BIGINT NULL,
    `user_id` BIGINT NOT NULL,
    `new_fragment_id` BIGINT NULL,
    `migrated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`legacy_fragment_id`),
    KEY `idx_legacy_memo_fragment_mapping_user_id` (`user_id`),
    KEY `idx_legacy_memo_fragment_mapping_group_id` (`legacy_group_id`),
    KEY `idx_legacy_memo_fragment_mapping_new_fragment_id` (`new_fragment_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET @has_memo_fragment := (
    SELECT COUNT(*)
    FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_fragment'
);

SET @has_fragment_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_fragment'
      AND COLUMN_NAME = 'id'
);

SET @has_fragment_group_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_fragment'
      AND COLUMN_NAME = 'group_id'
);
SET @has_fragment_memo_group_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_fragment'
      AND COLUMN_NAME = 'memo_group_id'
);
SET @has_fragment_week_record_id := (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME = 'memo_fragment'
      AND COLUMN_NAME = 'week_record_id'
);

SET @fragment_relation_available := IF(
    @has_fragment_group_id + @has_fragment_memo_group_id + @has_fragment_week_record_id > 0,
    1,
    0
);

SET @can_migrate_fragments := IF(
    @has_memo_fragment > 0 AND @has_fragment_id > 0 AND @fragment_relation_available = 1,
    1,
    0
);

SET @has_fragment_user_id := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'user_id'
);
SET @has_fragment_work_date := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'work_date'
);
SET @has_fragment_title := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'title'
);
SET @has_fragment_content := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'content'
);
SET @has_fragment_status := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'status'
);
SET @has_fragment_priority := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'priority'
);
SET @has_fragment_tag := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'tag'
);
SET @has_fragment_sort_order := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'sort_order'
);
SET @has_fragment_create_time := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'create_time'
);
SET @has_fragment_update_time := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'update_time'
);
SET @has_fragment_deleted := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'deleted'
);
SET @has_fragment_deleted_at := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment' AND COLUMN_NAME = 'deleted_at'
);

SET @expr_fragment_group_id := IF(
    @has_fragment_group_id = 1,
    "f.group_id",
    IF(@has_fragment_memo_group_id = 1, "f.memo_group_id", IF(@has_fragment_week_record_id = 1, "f.week_record_id", "NULL"))
);

SET @expr_fragment_user_id := IF(@has_fragment_user_id = 1, "f.user_id", "NULL");
SET @expr_fragment_work_date := IF(@has_fragment_work_date = 1, "f.work_date", "NULL");
SET @expr_fragment_title := IF(@has_fragment_title = 1, "f.title", "NULL");
SET @expr_fragment_content := IF(@has_fragment_content = 1, "f.content", "NULL");
SET @expr_fragment_status := IF(@has_fragment_status = 1, "f.status", "NULL");
SET @expr_fragment_priority := IF(@has_fragment_priority = 1, "f.priority", "NULL");
SET @expr_fragment_tag := IF(@has_fragment_tag = 1, "f.tag", "NULL");
SET @expr_fragment_sort_order := IF(@has_fragment_sort_order = 1, "f.sort_order", "NULL");
SET @expr_fragment_created_at := IF(@has_fragment_create_time = 1, "COALESCE(f.create_time, NOW())", "NOW()");
SET @expr_fragment_updated_at := IF(@has_fragment_update_time = 1, CONCAT("COALESCE(f.update_time, ", @expr_fragment_created_at, ")"), @expr_fragment_created_at);
SET @expr_fragment_deleted_mark_time := IF(
    @has_fragment_update_time = 1 AND @has_fragment_create_time = 1,
    "COALESCE(f.update_time, f.create_time, NOW())",
    IF(
        @has_fragment_update_time = 1,
        "COALESCE(f.update_time, NOW())",
        IF(@has_fragment_create_time = 1, "COALESCE(f.create_time, NOW())", "NOW()")
    )
);
SET @expr_fragment_deleted_at := IF(
    @has_fragment_deleted_at = 1,
    "f.deleted_at",
    IF(@has_fragment_deleted = 1, CONCAT("IF(IFNULL(f.deleted, 0) = 1, ", @expr_fragment_deleted_mark_time, ", NULL)"), "NULL")
);
SET @expr_fragment_filter := IF(
    @has_fragment_deleted_at = 1,
    "f.deleted_at IS NULL",
    IF(@has_fragment_deleted = 1, "IFNULL(f.deleted, 0) = 0", "1 = 1")
);

DROP TEMPORARY TABLE IF EXISTS `tmp_legacy_memo_fragments`;
CREATE TEMPORARY TABLE `tmp_legacy_memo_fragments` (
    `legacy_fragment_id` BIGINT NOT NULL,
    `legacy_group_id` BIGINT NULL,
    `user_id` BIGINT NULL,
    `work_date` DATE NULL,
    `title` VARCHAR(255) NULL,
    `content` TEXT NULL,
    `status` VARCHAR(32) NULL,
    `priority` VARCHAR(32) NULL,
    `tag` VARCHAR(64) NULL,
    `sort_order` INT NULL,
    `created_at` DATETIME NOT NULL,
    `updated_at` DATETIME NOT NULL,
    `deleted_at` DATETIME NULL,
    PRIMARY KEY (`legacy_fragment_id`),
    KEY `idx_tmp_legacy_memo_fragments_group_id` (`legacy_group_id`)
) ENGINE=InnoDB;

SET @insert_fragments_sql := IF(
    @can_migrate_fragments = 1,
    CONCAT(
        "INSERT INTO tmp_legacy_memo_fragments (legacy_fragment_id, legacy_group_id, user_id, work_date, title, content, status, priority, tag, sort_order, created_at, updated_at, deleted_at) ",
        "SELECT ",
        "f.id AS legacy_fragment_id, ",
        @expr_fragment_group_id, " AS legacy_group_id, ",
        @expr_fragment_user_id, " AS user_id, ",
        @expr_fragment_work_date, " AS work_date, ",
        @expr_fragment_title, " AS title, ",
        @expr_fragment_content, " AS content, ",
        @expr_fragment_status, " AS status, ",
        @expr_fragment_priority, " AS priority, ",
        @expr_fragment_tag, " AS tag, ",
        @expr_fragment_sort_order, " AS sort_order, ",
        @expr_fragment_created_at, " AS created_at, ",
        @expr_fragment_updated_at, " AS updated_at, ",
        @expr_fragment_deleted_at, " AS deleted_at ",
        "FROM memo_fragment f ",
        "WHERE ", @expr_fragment_filter
    ),
    "SELECT 'skip V7: memo_fragment or required columns not found'"
);

PREPARE stmt_insert_fragments FROM @insert_fragments_sql;
EXECUTE stmt_insert_fragments;
DEALLOCATE PREPARE stmt_insert_fragments;

DROP TEMPORARY TABLE IF EXISTS `tmp_ready_new_fragments`;
CREATE TEMPORARY TABLE `tmp_ready_new_fragments` AS
SELECT
    t.legacy_fragment_id,
    t.legacy_group_id,
    COALESCE(t.user_id, gm.user_id) AS user_id,
    gm.new_week_record_id AS week_record_id,
    COALESCE(t.work_date, DATE(t.created_at), CURDATE()) AS work_date,
    COALESCE(NULLIF(t.title, ''), '未命名碎片') AS title,
    COALESCE(t.content, '') AS content,
    COALESCE(NULLIF(t.status, ''), 'done') AS status,
    COALESCE(NULLIF(t.priority, ''), 'medium') AS priority,
    NULLIF(t.tag, '') AS tag,
    CASE
        WHEN t.sort_order IS NOT NULL AND t.sort_order > 0 THEN t.sort_order
        ELSE ROW_NUMBER() OVER (
            PARTITION BY gm.new_week_record_id
            ORDER BY t.created_at ASC, t.legacy_fragment_id ASC
        )
    END AS sort_order,
    COALESCE(t.created_at, NOW()) AS created_at,
    COALESCE(t.updated_at, COALESCE(t.created_at, NOW())) AS updated_at,
    t.deleted_at
FROM tmp_legacy_memo_fragments t
JOIN legacy_memo_group_mapping gm
  ON gm.legacy_group_id = t.legacy_group_id
WHERE gm.new_week_record_id IS NOT NULL;

SET @insert_new_fragments_sql := IF(
    @can_migrate_fragments = 1,
    "INSERT INTO memo_fragments (user_id, week_record_id, work_date, title, content, status, priority, tag, sort_order, created_at, updated_at, deleted_at)
     SELECT
         r.user_id,
         r.week_record_id,
         r.work_date,
         r.title,
         r.content,
         r.status,
         r.priority,
         r.tag,
         r.sort_order,
         r.created_at,
         r.updated_at,
         r.deleted_at
     FROM tmp_ready_new_fragments r
     LEFT JOIN memo_fragments mf
       ON mf.user_id = r.user_id
      AND mf.week_record_id = r.week_record_id
      AND mf.title = r.title
      AND mf.created_at = r.created_at
     WHERE mf.id IS NULL",
    "SELECT 'skip V7 new fragment insert'"
);

PREPARE stmt_insert_new_fragments FROM @insert_new_fragments_sql;
EXECUTE stmt_insert_new_fragments;
DEALLOCATE PREPARE stmt_insert_new_fragments;

SET @insert_fragment_mapping_sql := IF(
    @can_migrate_fragments = 1,
    "INSERT INTO legacy_memo_fragment_mapping (legacy_fragment_id, legacy_group_id, user_id, new_fragment_id, migrated_at)
     SELECT
         r.legacy_fragment_id,
         r.legacy_group_id,
         r.user_id,
         (
             SELECT mf.id
             FROM memo_fragments mf
             WHERE mf.user_id = r.user_id
               AND mf.week_record_id = r.week_record_id
               AND mf.title = r.title
               AND mf.created_at = r.created_at
             ORDER BY mf.id DESC
             LIMIT 1
         ) AS new_fragment_id,
         NOW() AS migrated_at
     FROM tmp_ready_new_fragments r
     ON DUPLICATE KEY UPDATE
         legacy_group_id = VALUES(legacy_group_id),
         user_id = VALUES(user_id),
         new_fragment_id = VALUES(new_fragment_id),
         migrated_at = VALUES(migrated_at)",
    "SELECT 'skip V7 mapping table update'"
);

PREPARE stmt_insert_fragment_mapping FROM @insert_fragment_mapping_sql;
EXECUTE stmt_insert_fragment_mapping;
DEALLOCATE PREPARE stmt_insert_fragment_mapping;

-- Post-migration summary output for quick check in Flyway logs.
SELECT
    'V7_migration_summary' AS check_name,
    (SELECT COUNT(*) FROM tmp_legacy_memo_fragments) AS legacy_fragment_rows_read,
    (SELECT COUNT(*) FROM tmp_ready_new_fragments) AS legacy_fragment_rows_resolved,
    (SELECT COUNT(*) FROM legacy_memo_fragment_mapping WHERE new_fragment_id IS NOT NULL) AS mapped_fragment_rows,
    (SELECT COUNT(*) FROM legacy_memo_fragment_mapping WHERE new_fragment_id IS NULL) AS unmapped_fragment_rows;
