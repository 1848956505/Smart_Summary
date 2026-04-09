-- 创建数据库
CREATE DATABASE IF NOT EXISTS smart_summary DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE smart_summary;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    avatar VARCHAR(500) COMMENT '用户头像URL',
    position VARCHAR(100) COMMENT '用户岗位',
    model_id VARCHAR(100) DEFAULT 'qwen2.5-7b-instruct' COMMENT '模型名称',
    api_key VARCHAR(500) COMMENT 'API密钥',
    base_url VARCHAR(500) DEFAULT 'http://localhost:8000' COMMENT '接口地址',
    temperature DOUBLE DEFAULT 0.7 COMMENT '生成随机性 0.0-1.5',
    max_tokens INT DEFAULT 2048 COMMENT '最大长度 512-4096',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_username (username),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 工作总结记录表
CREATE TABLE IF NOT EXISTS summary_records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    original_text TEXT NOT NULL COMMENT '用户输入的原始工作流水',
    summary_text TEXT NOT NULL COMMENT '生成的工作总结',
    style VARCHAR(20) NOT NULL COMMENT '风格：dingtalk/feishu/wechat',
    model_id VARCHAR(100) COMMENT '模型名称',
    api_key VARCHAR(500) COMMENT 'API密钥',
    base_url VARCHAR(500) COMMENT '接口地址',
    temperature DOUBLE COMMENT '生成随机性',
    max_tokens INT COMMENT '最大长度',
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_user_id (user_id),
    INDEX idx_create_time (create_time),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 测试数据
INSERT INTO users (username, password, email) VALUES ('test', 'test123', 'test@example.com');

-- 碎片记录文件夹
CREATE TABLE IF NOT EXISTS memo_folder (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    folder_name VARCHAR(100) NOT NULL,
    folder_order INT DEFAULT 0,
    is_collapsed TINYINT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_user_id (user_id),
    INDEX idx_folder_order (folder_order),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 周记录
CREATE TABLE IF NOT EXISTS memo_week_record (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    folder_id BIGINT NOT NULL,
    title VARCHAR(200) NOT NULL,
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'draft' COMMENT 'draft/generated/archived',
    summary_content LONGTEXT,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_user_id (user_id),
    INDEX idx_folder_id (folder_id),
    INDEX idx_week_range (week_start_date, week_end_date),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 工作碎片
CREATE TABLE IF NOT EXISTS memo_fragment (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    week_record_id BIGINT NOT NULL,
    work_date DATE NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    status VARCHAR(20) DEFAULT 'todo' COMMENT 'todo/doing/done/blocked',
    priority VARCHAR(20) DEFAULT 'medium' COMMENT 'low/medium/high',
    tag VARCHAR(50) DEFAULT '未分类',
    sort_order INT DEFAULT 0,
    create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    update_time DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    deleted TINYINT DEFAULT 0,
    INDEX idx_week_record_id (week_record_id),
    INDEX idx_work_date (work_date),
    INDEX idx_sort_order (sort_order),
    INDEX idx_deleted (deleted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
