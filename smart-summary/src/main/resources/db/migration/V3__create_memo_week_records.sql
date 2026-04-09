CREATE TABLE IF NOT EXISTS `memo_week_records` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `folder_id` BIGINT NOT NULL,
    `title` VARCHAR(255) NOT NULL,
    `week_start_date` DATE NOT NULL,
    `week_end_date` DATE NOT NULL,
    `status` VARCHAR(32) NOT NULL DEFAULT 'draft',
    `summary_content` LONGTEXT NULL,
    `version` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted_at` DATETIME NULL DEFAULT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_memo_week_records_folder_id` (`folder_id`),
    KEY `idx_memo_week_records_user_folder_week` (`user_id`, `folder_id`, `week_start_date`),
    KEY `idx_memo_week_records_deleted_at` (`deleted_at`),
    CONSTRAINT `fk_memo_week_records_folder_id`
        FOREIGN KEY (`folder_id`) REFERENCES `memo_folders` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
