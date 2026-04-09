package com.smartsummary.controller;

import com.smartsummary.entity.MemoFolder;
import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.service.CurrentUserService;
import com.smartsummary.service.MemoFolderService;
import com.smartsummary.service.MemoFragmentService;
import com.smartsummary.service.MemoWeekRecordService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/memo")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class MemoController {

    private final MemoFolderService memoFolderService;
    private final MemoWeekRecordService memoWeekRecordService;
    private final MemoFragmentService memoFragmentService;
    private final CurrentUserService currentUserService;

    @GetMapping("/folders")
    public Map<String, Object> listFolders() {
        Long userId = currentUserService.requireCurrentUserId();
        return success(memoFolderService.listByUserId(userId));
    }

    @PostMapping("/folders")
    public Map<String, Object> createFolder(@RequestBody FolderRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoFolder folder = memoFolderService.createFolder(userId, request.getName(), request.getSortOrder(), request.getIsCollapsed());
        return success(folder);
    }

    @PutMapping("/folders/{id}")
    public Map<String, Object> updateFolder(@PathVariable Long id, @RequestBody FolderRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoFolder folder = memoFolderService.getFolderDetail(userId, id);
        if (request.getName() != null) {
            folder = memoFolderService.renameFolder(userId, id, request.getName());
        }
        if (request.getSortOrder() != null) {
            folder = memoFolderService.updateSortOrder(userId, id, request.getSortOrder());
        }
        if (request.getIsCollapsed() != null) {
            folder = memoFolderService.updateCollapsed(userId, id, request.getIsCollapsed());
        }
        return success(folder);
    }

    @DeleteMapping("/folders/{id}")
    public Map<String, Object> deleteFolder(@PathVariable Long id) {
        Long userId = currentUserService.requireCurrentUserId();
        memoFolderService.deleteFolder(userId, id);
        return ok();
    }

    @GetMapping("/weeks")
    public Map<String, Object> listWeeks(@RequestParam Long folderId) {
        Long userId = currentUserService.requireCurrentUserId();
        List<MemoWeekRecord> weeks = memoWeekRecordService.listByFolderId(userId, folderId);
        List<Map<String, Object>> result = weeks.stream().map(this::toWeekWithStats).toList();
        return success(result);
    }

    @GetMapping("/weeks/{id}")
    public Map<String, Object> getWeek(@PathVariable Long id) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoWeekRecord week = memoWeekRecordService.getWeekRecordDetail(userId, id);
        return success(toWeekWithStats(week));
    }

    @PostMapping("/weeks")
    public Map<String, Object> createWeek(@RequestBody WeekRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoWeekRecord week = memoWeekRecordService.createWeekRecord(
                userId,
                request.getFolderId(),
                request.getTitle(),
                request.getWeekStartDate(),
                request.getWeekEndDate()
        );
        return success(week);
    }

    @PutMapping("/weeks/{id}")
    public Map<String, Object> updateWeek(@PathVariable Long id, @RequestBody WeekRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoWeekRecord week = memoWeekRecordService.updateWeekRecord(
                userId,
                id,
                request.getFolderId(),
                request.getTitle(),
                request.getWeekStartDate(),
                request.getWeekEndDate(),
                request.getStatus(),
                request.getSummaryContent()
        );
        return success(week);
    }

    @DeleteMapping("/weeks/{id}")
    public Map<String, Object> deleteWeek(@PathVariable Long id) {
        Long userId = currentUserService.requireCurrentUserId();
        memoWeekRecordService.deleteWeekRecord(userId, id);
        return ok();
    }

    @GetMapping("/fragments")
    public Map<String, Object> listFragments(
            @RequestParam(required = false) Long weekRecordId,
            @RequestParam(required = false) Long weekId
    ) {
        Long userId = currentUserService.requireCurrentUserId();
        Long targetWeekRecordId = Optional.ofNullable(weekRecordId).orElse(weekId);
        if (targetWeekRecordId == null) {
            return fail("缺少参数 weekRecordId");
        }
        return success(memoFragmentService.listByWeekRecordId(userId, targetWeekRecordId));
    }

    @PostMapping("/fragments")
    public Map<String, Object> createFragment(@RequestBody FragmentRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoFragment fragment = memoFragmentService.createFragment(
                userId,
                request.getWeekRecordId(),
                request.getWorkDate(),
                request.getTitle(),
                request.getContent(),
                request.getStatus(),
                request.getPriority(),
                request.getTag(),
                request.getSortOrder()
        );
        return success(fragment);
    }

    @PutMapping("/fragments/{id}")
    public Map<String, Object> updateFragment(@PathVariable Long id, @RequestBody FragmentRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoFragment fragment = memoFragmentService.updateFragment(
                userId,
                id,
                request.getWeekRecordId(),
                request.getWorkDate(),
                request.getTitle(),
                request.getContent(),
                request.getStatus(),
                request.getPriority(),
                request.getTag(),
                request.getSortOrder()
        );
        return success(fragment);
    }

    @DeleteMapping("/fragments/{id}")
    public Map<String, Object> deleteFragment(@PathVariable Long id) {
        Long userId = currentUserService.requireCurrentUserId();
        memoFragmentService.deleteFragment(userId, id);
        return ok();
    }

    @PostMapping("/weeks/{id}/generate-summary")
    public Map<String, Object> generateSummary(@PathVariable Long id, @RequestBody GenerateSummaryRequest request) {
        try {
            Long userId = currentUserService.requireCurrentUserId();
            String summary = memoWeekRecordService.generateWeeklySummary(
                    userId,
                    id,
                    request.getProjectName(),
                    request.getUserPosition()
            );
            List<MemoFragment> fragments = memoFragmentService.listByWeekRecordId(userId, id);
            return success(Map.of(
                    "weekRecordId", id,
                    "summary", summary,
                    "stats", buildStats(fragments)
            ));
        } catch (Exception e) {
            return fail(e.getMessage());
        }
    }

    @PostMapping("/weeks/{id}/save-summary")
    public Map<String, Object> saveSummary(@PathVariable Long id, @RequestBody SaveSummaryRequest request) {
        Long userId = currentUserService.requireCurrentUserId();
        MemoWeekRecord week = memoWeekRecordService.saveSummary(
                userId,
                id,
                Optional.ofNullable(request.getSummaryContent()).orElse(""),
                Optional.ofNullable(request.getStatus()).orElse("generated")
        );
        return success(week);
    }

    private Map<String, Object> toWeekWithStats(MemoWeekRecord week) {
        List<MemoFragment> fragments = memoFragmentService.listByWeekRecordId(week.getUserId(), week.getId());
        Map<String, Long> stats = buildStats(fragments);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("id", week.getId());
        result.put("userId", week.getUserId());
        result.put("folderId", week.getFolderId());
        result.put("title", week.getTitle());
        result.put("weekStartDate", week.getWeekStartDate());
        result.put("weekEndDate", week.getWeekEndDate());
        result.put("status", week.getStatus());
        result.put("summaryContent", week.getSummaryContent());
        result.put("fragmentCount", fragments.size());
        result.put("stats", stats);
        result.put("createTime", week.getCreatedAt());
        result.put("updateTime", week.getUpdatedAt());
        return result;
    }

    private Map<String, Long> buildStats(List<MemoFragment> fragments) {
        Map<String, Long> stats = new LinkedHashMap<>();
        stats.put("total", (long) fragments.size());
        stats.put("todo", fragments.stream().filter(f -> "todo".equalsIgnoreCase(f.getStatus())).count());
        stats.put("doing", fragments.stream().filter(f -> "doing".equalsIgnoreCase(f.getStatus())).count());
        stats.put("done", fragments.stream().filter(f -> "done".equalsIgnoreCase(f.getStatus())).count());
        stats.put("blocked", fragments.stream().filter(f -> "blocked".equalsIgnoreCase(f.getStatus())).count());
        return stats;
    }

    private Map<String, Object> ok() {
        return Map.of("success", true);
    }

    private Map<String, Object> fail(String message) {
        return Map.of("success", false, "message", message == null ? "操作失败" : message);
    }

    private Map<String, Object> success(Object data) {
        return Map.of("success", true, "data", data);
    }

    @Data
    public static class FolderRequest {
        private String name;
        private Integer sortOrder;
        private Integer isCollapsed;
    }

    @Data
    public static class WeekRequest {
        private Long folderId;
        private String title;
        private LocalDate weekStartDate;
        private LocalDate weekEndDate;
        private String status;
        private String summaryContent;
    }

    @Data
    public static class FragmentRequest {
        private Long weekRecordId;
        private LocalDate workDate;
        private String title;
        private String content;
        private String status;
        private String priority;
        private String tag;
        private Integer sortOrder;
    }

    @Data
    public static class GenerateSummaryRequest {
        private String projectName;
        private String userPosition;
    }

    @Data
    public static class SaveSummaryRequest {
        private String summaryContent;
        private String status;
    }
}
