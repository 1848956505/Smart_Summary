-- Evaluation result:
-- Existing table `memo_fragment` is not present in the current database snapshot.
-- The target model requires a new table with user scope and soft-delete timestamp.
-- Therefore this migration creates `memo_fragments`.

CREATE TABLE IF NOT EXISTS `memo_fragments` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `week_record_id` BIGINT NOT NULL,
    `work_date` DATE NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `content` TEXT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'todo',
    `priority` VARCHAR(32) NOT NULL DEFAULT 'medium',
    `tag` VARCHAR(64) NULL DEFAULT NULL,
    `sort_order` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_memo_fragments_user_id` (`user_id`),
    KEY `idx_memo_fragments_week_record_id` (`week_record_id`),
    KEY `idx_memo_fragments_user_week_work_date` (`user_id`, `week_record_id`, `work_date`),
    KEY `idx_memo_fragments_user_week_sort_order` (`user_id`, `week_record_id`, `sort_order`),
    KEY `idx_memo_fragments_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_memo_fragments_week_record_id`
        FOREIGN KEY (`week_record_id`) REFERENCES `memo_week_records` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
