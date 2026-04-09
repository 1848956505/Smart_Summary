# 数据库现状盘点（阶段一）

- 盘点时间：2026-04-07
- 数据库：`smart_summary`
- 采集方式：`information_schema` + `SHOW CREATE TABLE`

## 1. 当前库表清单（真实）

```text
memo_folder
summary_records
users
```

## 2. 重点表状态（按任务要求）

| 表名 | 是否存在 | 备注 |
|---|---|---|
| `users` | 是 | 当前在线表 |
| `summary_records` | 是 | 当前在线表 |
| `memo_group` | 否 | 当前库中不存在 |
| `memo_fragment` | 否 | 当前库中不存在 |

补充：当前库中也不存在 `memo_week_record`。

## 3. 字段清单（字段名/类型/默认值/主键）

### 3.1 `users`

| 字段 | 类型 | 可空 | 默认值 | 键 | 额外 |
|---|---|---|---|---|---|
| id | bigint | NO | NULL | PRI | auto_increment |
| username | varchar(50) | NO | NULL | UNI |  |
| password | varchar(255) | NO | NULL |  |  |
| email | varchar(100) | YES | NULL |  |  |
| create_time | datetime | YES | CURRENT_TIMESTAMP |  | DEFAULT_GENERATED |
| update_time | datetime | YES | CURRENT_TIMESTAMP |  | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
| deleted | tinyint | YES | 0 | MUL |  |
| avatar | varchar(500) | YES | NULL |  |  |
| position | varchar(100) | YES | NULL |  |  |
| model_id | varchar(100) | YES | qwen2.5-7b-instruct |  |  |
| api_key | varchar(500) | YES | NULL |  |  |
| base_url | varchar(500) | YES | http://localhost:8000 |  |  |
| temperature | double | YES | 0.7 |  |  |
| max_tokens | int | YES | 2048 |  |  |

### 3.2 `summary_records`

| 字段 | 类型 | 可空 | 默认值 | 键 | 额外 |
|---|---|---|---|---|---|
| id | bigint | NO | NULL | PRI | auto_increment |
| user_id | bigint | NO | NULL | MUL |  |
| original_text | text | NO | NULL |  |  |
| summary_text | text | NO | NULL |  |  |
| style | varchar(20) | NO | NULL |  |  |
| model_id | varchar(100) | YES | NULL |  |  |
| api_key | varchar(500) | YES | NULL |  |  |
| base_url | varchar(500) | YES | NULL |  |  |
| temperature | double | YES | NULL |  |  |
| max_tokens | int | YES | NULL |  |  |
| create_time | datetime | YES | CURRENT_TIMESTAMP | MUL | DEFAULT_GENERATED |
| update_time | datetime | YES | CURRENT_TIMESTAMP |  | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
| deleted | tinyint | YES | 0 | MUL |  |

### 3.3 `memo_folder`

| 字段 | 类型 | 可空 | 默认值 | 键 | 额外 |
|---|---|---|---|---|---|
| id | bigint | NO | NULL | PRI | auto_increment |
| user_id | bigint | NO | NULL | MUL |  |
| name | varchar(255) | NO | NULL |  |  |
| parent_id | bigint | YES | NULL | MUL |  |
| create_time | datetime | YES | CURRENT_TIMESTAMP |  | DEFAULT_GENERATED |
| update_time | datetime | YES | CURRENT_TIMESTAMP |  | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |
| deleted | tinyint | YES | 0 | MUL |  |

## 4. 索引信息（真实）

### 4.1 `users`

| 索引名 | 唯一 | 列序 |
|---|---|---|
| PRIMARY | 是 | id |
| username | 是 | username |
| idx_username | 否 | username |
| idx_deleted | 否 | deleted |

### 4.2 `summary_records`

| 索引名 | 唯一 | 列序 |
|---|---|---|
| PRIMARY | 是 | id |
| idx_user_id | 否 | user_id |
| idx_create_time | 否 | create_time |
| idx_deleted | 否 | deleted |

### 4.3 `memo_folder`

| 索引名 | 唯一 | 列序 |
|---|---|---|
| PRIMARY | 是 | id |
| idx_user_id | 否 | user_id |
| idx_parent_id | 否 | parent_id |
| idx_deleted | 否 | deleted |

## 5. 外键信息（真实）

当前库没有任何外键约束（`KEY_COLUMN_USAGE` 中无 `REFERENCED_TABLE_NAME` 记录）。

## 6. 当前建表 SQL（SHOW CREATE TABLE）

### 6.1 `users`

```sql
CREATE TABLE `users` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted` tinyint DEFAULT '0',
  `avatar` varchar(500) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  `model_id` varchar(100) DEFAULT 'qwen2.5-7b-instruct',
  `api_key` varchar(500) DEFAULT NULL,
  `base_url` varchar(500) DEFAULT 'http://localhost:8000',
  `temperature` double DEFAULT '0.7',
  `max_tokens` int DEFAULT '2048',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `idx_username` (`username`),
  KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### 6.2 `summary_records`

```sql
CREATE TABLE `summary_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `original_text` text NOT NULL COMMENT '用户输入的原始工作流水',
  `summary_text` text NOT NULL COMMENT '生成的工作总结',
  `style` varchar(20) NOT NULL COMMENT '风格：dingtalk/feishu/wechat',
  `model_id` varchar(100) DEFAULT NULL COMMENT '模型名称',
  `api_key` varchar(500) DEFAULT NULL COMMENT 'API密钥',
  `base_url` varchar(500) DEFAULT NULL COMMENT '接口地址',
  `temperature` double DEFAULT NULL COMMENT '生成随机性',
  `max_tokens` int DEFAULT NULL COMMENT '最大长度',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

### 6.3 `memo_folder`

```sql
CREATE TABLE `memo_folder` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL COMMENT '所属用户ID',
  `name` varchar(255) NOT NULL COMMENT '文件夹名称',
  `parent_id` bigint DEFAULT NULL COMMENT '父文件夹ID',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted` tinyint DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_parent_id` (`parent_id`),
  KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

## 7. 盘点结论

1. 数据库真实结构与 `smart-summary/sql/schema.sql` 不一致（尤其 `memo_folder` 字段定义差异明显）。
2. 当前 DB 中不存在 `memo_group`、`memo_fragment`、`memo_week_record` 三张表。
3. 现有 memo 相关数据结构并未达到“文件夹 + 周记录 + 碎片”三层模型，后续迁移必须先补齐新表（Flyway）。
