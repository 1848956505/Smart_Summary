# Memo 模型差异分析（阶段一）

- 范围：`smart-summary/src/main/java` + `smart-summary/sql` + `smart-summary-web/src`
- 目标：梳理 Entity / Repository / Controller 与真实 DB 的映射关系，识别字段与语义不一致点

## 1. 全局检索结论（指定关键词）

关键词检索：`MemoGroup`, `MemoFragment`, `SummaryRecord`, `groupId`, `folderName`, `weekDate`, `folder_name`, `memo_group`, `memo_fragment`

结论：
1. 代码中不存在 `MemoGroup` 类。
2. 代码大量使用 `MemoFragment`（Entity/Service/Controller），映射表为 `memo_fragment`。
3. 代码存在 `folderName` 字段（Java 驼峰），SQL 文件存在 `folder_name`（下划线）。
4. DB 实际没有 `memo_group` / `memo_fragment` 表；但代码和 SQL 文件依赖这两类语义。

## 2. Entity ↔ Table 映射

| Entity | 注解 TableName | 真实 DB 表是否存在 | 备注 |
|---|---|---|---|
| `User` | `users` | 是 | 基本一致 |
| `SummaryRecord` | `summary_records` | 是 | 基本一致 |
| `MemoFolder` | `memo_folder` | 是 | 字段不一致（见下） |
| `MemoWeekRecord` | `memo_week_record` | 否 | 代码存在，DB 缺表 |
| `MemoFragment` | `memo_fragment` | 否 | 代码存在，DB 缺表 |

## 3. Repository/Mapper 映射与查询字段

Repository 均为 MyBatis-Plus `BaseMapper`：

| Repository | Entity | 表 |
|---|---|---|
| `UserRepository` | `User` | `users` |
| `SummaryRecordRepository` | `SummaryRecord` | `summary_records` |
| `MemoFolderRepository` | `MemoFolder` | `memo_folder` |
| `MemoWeekRecordRepository` | `MemoWeekRecord` | `memo_week_record` |
| `MemoFragmentRepository` | `MemoFragment` | `memo_fragment` |

主要查询字段（按 Service/Controller）：
1. `MemoFolder`: `userId`, `folderOrder`, `createTime`
2. `MemoWeekRecord`: `userId`, `folderId`, `weekStartDate`, `createTime`
3. `MemoFragment`: `weekRecordId`, `workDate`, `sortOrder`, `createTime`
4. `SummaryRecord`: `userId`, `createTime`

## 4. Controller 使用字段清单（memo 主链路）

文件：`MemoController`

1. 文件夹接口：
- 读取/写入：`id`, `userId`, `folderName`, `folderOrder`, `isCollapsed`

2. 周记录接口：
- 读取/写入：`id`, `userId`, `folderId`, `title`, `weekStartDate`, `weekEndDate`, `status`, `summaryContent`

3. 碎片接口：
- 读取/写入：`id`, `weekRecordId`, `workDate`, `title`, `content`, `status`, `priority`, `tag`, `sortOrder`

## 5. 字段与表结构不一致问题清单（核心）

###[P0] `memo_folder` 字段严重不匹配

- 代码实体（`MemoFolder`）字段：`folder_name` 语义（`folderName`）、`folder_order` 语义（`folderOrder`）、`is_collapsed` 语义（`isCollapsed`）
- 真实 DB 字段：`name`, `parent_id`
- 直接影响：`/api/memo/folders` 相关 CRUD 可能在运行时出现 SQL 字段不存在或查询结果语义错位。

###[P0] `memo_week_record` 缺表

- `MemoWeekRecord` Entity + Service + Controller 全链路存在。
- 真实 DB 不存在 `memo_week_record`，所有周记录接口实际不可落库。

###[P0] `memo_fragment` 缺表

- `MemoFragment` Entity + Service + Controller 全链路存在。
- 真实 DB 不存在 `memo_fragment`，所有碎片接口实际不可落库。

###[P1] 代码语义与“旧结构 memo_group/memo_fragment”不一致且未兼容

- 代码已偏向“folder/week/fragment”三层语义。
- 但 DB 仅有旧版单层 `memo_folder(name,parent_id)`，且无迁移脚本执行痕迹。

###[P1] 软删除规范不一致

- 当前实现是 `deleted`（`@TableLogic`）而非 `deleted_at is null`。
- 你要求“默认过滤 `deleted_at is null`”，当前模型不满足，需要在重构设计阶段统一软删策略。

###[P1] user_id 约束未覆盖全部查询

- 许多查询带 `userId`（如 folder/week）。
- 但部分碎片接口仅靠 `weekId` 或 `id`（例如 `listFragments(weekId)`, `updateFragment(id)`, `deleteFragment(id)`），未显式按 `user_id` 兜底校验。

## 6. 仍依赖旧语义的接口/代码点

1. SQL 文件中的 `memo_folder` 仍带旧版字段历史痕迹与新版字段定义冲突（`sql/schema.sql` 与真实 DB 不一致）。
2. 前端 `MemosView` / `MemoSidebar` 使用 `folderName`，与真实 DB 的 `name` 不一致（依赖后端对象字段转换才能工作）。
3. 项目中不存在 `memo_group` 实体/仓库，说明“旧语义”已经半移除，但数据库并未完整迁移到新模型，处于中间态。

## 7. 结论（阶段一）

当前状态是“代码已前倾到新模型，数据库仍停在旧/中间模型”，存在明显漂移。  
后续必须按 Flyway 路径完成：新表建模 -> 数据迁移 -> 代码切换 -> 联调 -> 旧表归档，避免继续扩大语义断层。
