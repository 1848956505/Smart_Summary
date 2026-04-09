# Memo 迁移核对清单（阶段三）

本清单用于在执行 `V6`、`V7` 后快速确认是否丢数据、是否出现孤儿数据。

## 1. 总量核对

```sql
-- 旧 group 条数 vs 新 week_records 条数（迁移映射视角）
SELECT
  (SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_group') AS has_legacy_memo_group_table,
  (SELECT COUNT(*) FROM legacy_memo_group_mapping) AS mapped_group_rows,
  (SELECT COUNT(*) FROM legacy_memo_group_mapping WHERE new_week_record_id IS NOT NULL) AS mapped_to_week_rows,
  (SELECT COUNT(*) FROM memo_week_records WHERE deleted_at IS NULL) AS new_week_records_rows;

-- 旧 fragment 条数 vs 新 fragments 条数（迁移映射视角）
SELECT
  (SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'memo_fragment') AS has_legacy_memo_fragment_table,
  (SELECT COUNT(*) FROM legacy_memo_fragment_mapping) AS mapped_fragment_rows,
  (SELECT COUNT(*) FROM legacy_memo_fragment_mapping WHERE new_fragment_id IS NOT NULL) AS mapped_to_new_fragment_rows,
  (SELECT COUNT(*) FROM memo_fragments WHERE deleted_at IS NULL) AS new_fragments_rows;
```

## 2. 用户维度一致性核对

```sql
-- 按用户核对 group -> week_record 迁移量
SELECT
  gm.user_id,
  COUNT(*) AS legacy_group_count,
  SUM(CASE WHEN gm.new_week_record_id IS NOT NULL THEN 1 ELSE 0 END) AS mapped_week_count
FROM legacy_memo_group_mapping gm
GROUP BY gm.user_id
ORDER BY gm.user_id;

-- 按用户核对 fragment 迁移量
SELECT
  fm.user_id,
  COUNT(*) AS legacy_fragment_count,
  SUM(CASE WHEN fm.new_fragment_id IS NOT NULL THEN 1 ELSE 0 END) AS mapped_fragment_count
FROM legacy_memo_fragment_mapping fm
GROUP BY fm.user_id
ORDER BY fm.user_id;
```

## 3. 关联完整性核对（脏数据检查）

```sql
-- week_record 是否存在空 folder_id
SELECT COUNT(*) AS week_records_without_folder
FROM memo_week_records
WHERE folder_id IS NULL;

-- week_record 的 folder_id 是否指向不存在 folder
SELECT COUNT(*) AS week_records_invalid_folder_fk
FROM memo_week_records w
LEFT JOIN memo_folders f ON f.id = w.folder_id
WHERE f.id IS NULL;

-- fragments 是否存在空 week_record_id
SELECT COUNT(*) AS fragments_without_week_record
FROM memo_fragments
WHERE week_record_id IS NULL;

-- fragments 的 week_record_id 是否指向不存在 week_record
SELECT COUNT(*) AS fragments_invalid_week_record_fk
FROM memo_fragments m
LEFT JOIN memo_week_records w ON w.id = m.week_record_id
WHERE w.id IS NULL;
```

## 4. 未映射数据定位

```sql
-- 未成功映射到新 week_record 的 legacy group
SELECT *
FROM legacy_memo_group_mapping
WHERE new_week_record_id IS NULL
ORDER BY legacy_group_id
LIMIT 100;

-- 未成功映射到新 fragment 的 legacy fragment
SELECT *
FROM legacy_memo_fragment_mapping
WHERE new_fragment_id IS NULL
ORDER BY legacy_fragment_id
LIMIT 100;
```

## 5. 验收建议阈值

1. `legacy_memo_group_mapping.new_week_record_id IS NULL` 数量应为 0（或有明确可解释例外）。
2. `legacy_memo_fragment_mapping.new_fragment_id IS NULL` 数量应为 0（或有明确可解释例外）。
3. `week_records_without_folder` 必须为 0。
4. `fragments_without_week_record` 必须为 0。
5. 用户维度上，迁移前后行数差异必须有书面解释（如软删过滤、非法脏数据剔除）。

## 6. 当前环境特别说明

根据阶段一盘点，当前 `smart_summary` 库并不存在 `memo_group` / `memo_fragment`。  
因此在当前环境执行 `V6` / `V7` 时，预计结果是“脚本可执行但迁移 0 行”，这属于预期行为。
