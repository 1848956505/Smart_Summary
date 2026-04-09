-- Baseline schema for existing production structure before memo refactor.
-- This baseline captures the currently observed schema in smart_summary.

CREATE TABLE IF NOT EXISTS `users` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(50) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `email` VARCHAR(100) DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    `avatar` VARCHAR(500) DEFAULT NULL,
    `position` VARCHAR(100) DEFAULT NULL,
    `model_id` VARCHAR(100) DEFAULT 'qwen2.5-7b-instruct',
    `api_key` VARCHAR(500) DEFAULT NULL,
    `base_url` VARCHAR(500) DEFAULT 'http://localhost:8000',
    `temperature` DOUBLE DEFAULT 0.7,
    `max_tokens` INT DEFAULT 2048,
    PRIMARY KEY (`id`),
    UNIQUE KEY `username` (`username`),
    KEY `idx_username` (`username`),
    KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `summary_records` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `original_text` TEXT NOT NULL,
    `summary_text` TEXT NOT NULL,
    `style` VARCHAR(20) NOT NULL,
    `model_id` VARCHAR(100) DEFAULT NULL,
    `api_key` VARCHAR(500) DEFAULT NULL,
    `base_url` VARCHAR(500) DEFAULT NULL,
    `temperature` DOUBLE DEFAULT NULL,
    `max_tokens` INT DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_create_time` (`create_time`),
    KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS `memo_folder` (
    `id` BIGINT NOT NULL AUTO_INCREMENT,
    `user_id` BIGINT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `parent_id` BIGINT DEFAULT NULL,
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `deleted` TINYINT DEFAULT 0,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    KEY `idx_parent_id` (`parent_id`),
    KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
