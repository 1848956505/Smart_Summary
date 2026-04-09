USE smart_summary;

-- 以 id=1 的用户作为演示账号，若不存在请先创建用户
SET @uid := 1;

INSERT INTO memo_folder (user_id, folder_name, folder_order, is_collapsed, deleted)
VALUES
(@uid, '毕设开发', 1, 0, 0),
(@uid, '论文撰写', 2, 0, 0),
(@uid, '算法实验', 3, 1, 0);

SET @folder_bys := (SELECT id FROM memo_folder WHERE user_id=@uid AND folder_name='毕设开发' ORDER BY id DESC LIMIT 1);
SET @week_start := DATE_SUB(CURDATE(), INTERVAL (WEEKDAY(CURDATE())) DAY);
SET @week_end := DATE_ADD(@week_start, INTERVAL 6 DAY);

INSERT INTO memo_week_record (user_id, folder_id, title, week_start_date, week_end_date, status, summary_content, deleted)
VALUES
(@uid, @folder_bys, CONCAT(@week_start, '~', @week_end, ' 工作碎片'), @week_start, @week_end, 'draft', '', 0);

SET @week_id := (SELECT id FROM memo_week_record WHERE user_id=@uid AND folder_id=@folder_bys ORDER BY id DESC LIMIT 1);

INSERT INTO memo_fragment (week_record_id, work_date, title, content, status, priority, tag, sort_order, deleted)
VALUES
(@week_id, @week_start, '完成碎片记录本页面骨架', '搭建左侧目录树和右侧内容区布局，完成主交互流转。', 'done', 'high', '开发', 1, 0),
(@week_id, DATE_ADD(@week_start, INTERVAL 1 DAY), '联调周记录接口', '完成 week/fragments 的前后端联调与异常提示处理。', 'doing', 'medium', '接口', 2, 0),
(@week_id, DATE_ADD(@week_start, INTERVAL 2 DAY), '修复导出兼容性问题', '定位 PDF 导出样式错位问题，已确认复现路径。', 'blocked', 'medium', '调试', 3, 0),
(@week_id, DATE_ADD(@week_start, INTERVAL 3 DAY), '阅读相关文献', '阅读两篇关于交互式工作流记录的论文并整理笔记。', 'done', 'low', '学习', 4, 0);

