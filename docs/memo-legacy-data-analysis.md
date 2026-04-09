# 旧数据抽样分析（阶段一）

- 目标表：`memo_group`、`memo_fragment`
- 实际库：`smart_summary`
- 采样时间：2026-04-07

## 1. 抽样执行结果

执行存在性检查：

```sql
SELECT 'memo_group_exists', COUNT(*)
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='smart_summary' AND TABLE_NAME='memo_group';

SELECT 'memo_fragment_exists', COUNT(*)
FROM information_schema.TABLES
WHERE TABLE_SCHEMA='smart_summary' AND TABLE_NAME='memo_fragment';
```

结果：
- `memo_group_exists = 0`
- `memo_fragment_exists = 0`

补充检查：
- `memo_week_record` 也不存在。
- 当前仅存在 `memo_folder`，且行数为 `0`（空表）。

## 2. 对任务问题逐项回答

### 2.1 `memo_group` 是否更像周记录？

无法直接判断。原因是该表在当前库不存在，且无样本数据可抽。

### 2.2 是否存在文件夹语义字段？

在当前仅存的 `memo_folder` 表中存在 `name` 与 `parent_id`，这是“树形目录”语义，不是“周记录”语义。

### 2.3 是否存在“一条 group 对应一周碎片”关系？

无法验证。`memo_group` 与 `memo_fragment` 两张旧表均不存在，`memo_folder` 也无数据。

### 2.4 是否存在脏数据/空字段/重复数据？

在目标旧表上无法评估（表缺失）。  
在可见 `memo_folder` 上无法评估（空表）。

## 3. 代码与 SQL 旁证（非数据样本）

虽然当前 DB 无旧数据，但从代码/SQL 可见以下历史痕迹：

1. 代码已引入三层模型实体：`MemoFolder`、`MemoWeekRecord`、`MemoFragment`。
2. `sql/schema.sql` 包含 `memo_week_record` 与 `memo_fragment` 建表语句（说明目标方向明确）。
3. 真实 DB 尚未落地上述表（说明迁移脚本或执行流程未闭环）。

## 4. 迁移规则建议（在“当前库无旧数据”前提下）

1. **默认规则**：按“无历史数据”路径迁移。
- 先用 Flyway 建立新表：`memo_folders`、`memo_week_records`、`memo_fragments`（遵循你定义的命名）。
- 暂不执行旧数据搬运 SQL（或以空迁移脚本保留流程）。

2. **若后续拿到历史库备份**：
- 增加 Flyway 数据迁移脚本，将旧 `memo_group/memo_fragment` 映射到新三层结构。
- 映射建议：
  - 先落 `memo_folders`（按用户/目录名去重）
  - 再落 `memo_week_records`（从 group 解析周区间）
  - 最后落 `memo_fragments`（保留原排序、状态、标签）

3. **质量门槛建议**：
- 缺失关键字段（`user_id`、时间范围）时，写入迁移异常表，不静默丢弃。
- 迁移后做三类校验：行数校验、用户维度校验、抽样内容校验。

## 5. 阶段一结论

当前环境无法进行“旧表数据样本分析”，因为旧表本身不在库中。  
这本身就是关键盘点结果：当前库处于“历史结构缺失 + 新结构未完整落地”的迁移断档态，后续必须用 Flyway 补齐结构与迁移链路。
