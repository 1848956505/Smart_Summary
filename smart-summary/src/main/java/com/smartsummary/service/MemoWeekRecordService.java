package com.smartsummary.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.smartsummary.entity.MemoFolder;
import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.entity.SummaryRecord;
import com.smartsummary.entity.User;
import com.smartsummary.repository.MemoFolderRepository;
import com.smartsummary.repository.MemoWeekRecordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.io.IOException;
import java.time.DayOfWeek;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class MemoWeekRecordService extends ServiceImpl<MemoWeekRecordRepository, MemoWeekRecord> {

    private final MemoWeekRecordRepository memoWeekRecordRepository;
    private final MemoFolderRepository memoFolderRepository;
    private final MemoFragmentService memoFragmentService;
    private final LlmService llmService;
    private final UserService userService;
    private final SummaryRecordService summaryRecordService;

    public List<MemoWeekRecord> listByFolderId(Long userId, Long folderId) {
        ensureFolderOwnership(userId, folderId);
        return memoWeekRecordRepository.findActiveByUserAndFolder(userId, folderId);
    }

    public MemoWeekRecord createWeekRecord(Long userId, Long folderId, String title, LocalDate weekStartDate, LocalDate weekEndDate) {
        ensureFolderOwnership(userId, folderId);
        LocalDate start = weekStartDate;
        LocalDate end = weekEndDate;
        if (start == null || end == null) {
            LocalDate today = LocalDate.now();
            start = today.with(DayOfWeek.MONDAY);
            end = today.with(DayOfWeek.SUNDAY);
        }

        MemoWeekRecord record = new MemoWeekRecord();
        record.setUserId(userId);
        record.setFolderId(folderId);
        record.setTitle((title == null || title.isBlank()) ? String.format("%s~%s Weekly Notes", start, end) : title);
        record.setWeekStartDate(start);
        record.setWeekEndDate(end);
        record.setStatus("draft");
        record.setSummaryContent("");
        record.setVersion(0);
        record.setCreatedAt(LocalDateTime.now());
        record.setUpdatedAt(LocalDateTime.now());
        save(record);
        return record;
    }

    public MemoWeekRecord getWeekRecordDetail(Long userId, Long weekRecordId) {
        MemoWeekRecord record = getOne(new LambdaQueryWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getId, weekRecordId)
                .eq(MemoWeekRecord::getUserId, userId)
                .isNull(MemoWeekRecord::getDeletedAt));
        if (record == null) {
            throw new RuntimeException("Week record not found");
        }
        return record;
    }

    public MemoWeekRecord updateWeekRecord(Long userId, Long weekRecordId, Long folderId, String title,
                                           LocalDate weekStartDate, LocalDate weekEndDate, String status,
                                           String summaryContent) {
        MemoWeekRecord current = getWeekRecordDetail(userId, weekRecordId);
        Long targetFolderId = folderId != null ? folderId : current.getFolderId();
        ensureFolderOwnership(userId, targetFolderId);

        if (folderId != null) current.setFolderId(folderId);
        if (title != null) current.setTitle(title);
        if (weekStartDate != null) current.setWeekStartDate(weekStartDate);
        if (weekEndDate != null) current.setWeekEndDate(weekEndDate);
        if (status != null) current.setStatus(status);
        if (summaryContent != null) current.setSummaryContent(summaryContent);
        current.setUpdatedAt(LocalDateTime.now());

        update(new LambdaUpdateWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getId, weekRecordId)
                .eq(MemoWeekRecord::getUserId, userId)
                .isNull(MemoWeekRecord::getDeletedAt)
                .set(MemoWeekRecord::getFolderId, current.getFolderId())
                .set(MemoWeekRecord::getTitle, current.getTitle())
                .set(MemoWeekRecord::getWeekStartDate, current.getWeekStartDate())
                .set(MemoWeekRecord::getWeekEndDate, current.getWeekEndDate())
                .set(MemoWeekRecord::getStatus, current.getStatus())
                .set(MemoWeekRecord::getSummaryContent, current.getSummaryContent())
                .set(MemoWeekRecord::getUpdatedAt, current.getUpdatedAt()));
        return getWeekRecordDetail(userId, weekRecordId);
    }

    @Transactional
    public void deleteWeekRecord(Long userId, Long weekRecordId) {
        MemoWeekRecord current = getWeekRecordDetail(userId, weekRecordId);
        memoFragmentService.softDeleteByWeekRecord(userId, current.getId());

        update(new LambdaUpdateWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getId, weekRecordId)
                .eq(MemoWeekRecord::getUserId, userId)
                .isNull(MemoWeekRecord::getDeletedAt)
                .set(MemoWeekRecord::getDeletedAt, LocalDateTime.now())
                .set(MemoWeekRecord::getUpdatedAt, LocalDateTime.now()));
    }

    @Transactional
    public String generateWeeklySummary(Long userId, Long weekRecordId, String projectName, String userPosition) {
        MemoWeekRecord weekRecord = getWeekRecordDetail(userId, weekRecordId);
        List<MemoFragment> fragments = memoFragmentService.listByWeekRecordId(userId, weekRecordId);
        if (fragments.isEmpty()) {
            throw new RuntimeException("No fragments found for the selected week");
        }

        String promptInput = buildWeeklySummaryInput(weekRecord, fragments, projectName, userPosition);
        LlmService.UserConfig userConfig = buildUserConfig(userId);
        String summary;
        try {
            summary = llmService.generateWeeklySummary(promptInput, userConfig);
        } catch (IOException e) {
            throw new RuntimeException("生成周报失败: " + e.getMessage(), e);
        }

        saveSummary(userId, weekRecordId, summary, "generated");
        upsertSummaryRecord(userId, weekRecord, summary, userConfig);
        return summary;
    }

    @Transactional
    public MemoWeekRecord saveSummary(Long userId, Long weekRecordId, String summaryContent, String status) {
        MemoWeekRecord weekRecord = getWeekRecordDetail(userId, weekRecordId);
        weekRecord.setSummaryContent(summaryContent == null ? "" : summaryContent);
        weekRecord.setStatus(status == null || status.isBlank() ? "generated" : status);
        weekRecord.setUpdatedAt(LocalDateTime.now());

        update(new LambdaUpdateWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getId, weekRecordId)
                .eq(MemoWeekRecord::getUserId, userId)
                .isNull(MemoWeekRecord::getDeletedAt)
                .set(MemoWeekRecord::getSummaryContent, weekRecord.getSummaryContent())
                .set(MemoWeekRecord::getStatus, weekRecord.getStatus())
                .set(MemoWeekRecord::getUpdatedAt, weekRecord.getUpdatedAt()));

        if (!weekRecord.getSummaryContent().isBlank()) {
            upsertSummaryRecord(userId, weekRecord, weekRecord.getSummaryContent(), buildUserConfig(userId));
        }
        return getWeekRecordDetail(userId, weekRecordId);
    }

    private void upsertSummaryRecord(Long userId, MemoWeekRecord weekRecord, String summary, LlmService.UserConfig userConfig) {
        String originalText = memoFragmentService.listByWeekRecordId(userId, weekRecord.getId()).stream()
                .sorted(Comparator.comparing(MemoFragment::getWorkDate).thenComparing(MemoFragment::getSortOrder, Comparator.nullsLast(Integer::compareTo)))
                .map(f -> String.format("[%s][%s][%s] %s: %s",
                        Optional.ofNullable(f.getWorkDate()).map(LocalDate::toString).orElse(""),
                        Optional.ofNullable(f.getStatus()).orElse("done"),
                        Optional.ofNullable(f.getTag()).orElse("uncategorized"),
                        Optional.ofNullable(f.getTitle()).orElse(""),
                        Optional.ofNullable(f.getContent()).orElse("")))
                .collect(Collectors.joining("\n"));

        SummaryRecord latest = summaryRecordService.getOne(new LambdaQueryWrapper<SummaryRecord>()
                .eq(SummaryRecord::getUserId, userId)
                .eq(SummaryRecord::getSourceWeekRecordId, weekRecord.getId())
                .orderByDesc(SummaryRecord::getCreateTime)
                .last("LIMIT 1"));

        if (latest == null) {
            SummaryRecord record = new SummaryRecord();
            record.setUserId(userId);
            record.setSourceWeekRecordId(weekRecord.getId());
            record.setOriginalText(originalText);
            record.setSummaryText(summary);
            record.setStyle("weekly");
            record.setModelId(userConfig.getModelId());
            record.setApiKey(userConfig.getApiKey());
            record.setBaseUrl(userConfig.getBaseUrl());
            record.setTemperature(userConfig.getTemperature());
            record.setMaxTokens(userConfig.getMaxTokens());
            summaryRecordService.save(record);
        } else {
            latest.setOriginalText(originalText);
            latest.setSummaryText(summary);
            latest.setModelId(userConfig.getModelId());
            latest.setApiKey(userConfig.getApiKey());
            latest.setBaseUrl(userConfig.getBaseUrl());
            latest.setTemperature(userConfig.getTemperature());
            latest.setMaxTokens(userConfig.getMaxTokens());
            summaryRecordService.updateById(latest);
        }
    }

    private void ensureFolderOwnership(Long userId, Long folderId) {
        if (memoFolderRepository.selectCount(new LambdaQueryWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)) == 0) {
            throw new RuntimeException("Folder not found");
        }
    }

    private LlmService.UserConfig buildUserConfig(Long userId) {
        User user = userService.getById(userId);
        if (user == null) {
            throw new RuntimeException("User not found");
        }

        LlmService.UserConfig config = new LlmService.UserConfig();
        config.setBaseUrl(user.getBaseUrl());
        config.setModelId(user.getModelId());
        config.setApiKey(user.getApiKey());
        config.setTemperature(user.getTemperature());
        config.setMaxTokens(user.getMaxTokens());
        return config;
    }

    private String buildWeeklySummaryInput(MemoWeekRecord weekRecord, List<MemoFragment> fragments, String projectName, String userPosition) {
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
        String fragmentLines = fragments.stream()
                .sorted(Comparator.comparing(MemoFragment::getWorkDate).thenComparing(MemoFragment::getSortOrder, Comparator.nullsLast(Integer::compareTo)))
                .map(f -> String.format("- [%s][%s][%s] %s: %s",
                        Optional.ofNullable(f.getWorkDate()).map(d -> d.format(formatter)).orElse(""),
                        Optional.ofNullable(f.getStatus()).orElse("done"),
                        Optional.ofNullable(f.getTag()).orElse("uncategorized"),
                        Optional.ofNullable(f.getTitle()).orElse(""),
                        Optional.ofNullable(f.getContent()).orElse("")))
                .collect(Collectors.joining("\n"));

        return String.format("""
                Week Range: %s to %s
                Week Record: %s
                Project: %s
                Position: %s

                Fragments:
                %s
                """,
                weekRecord.getWeekStartDate(),
                weekRecord.getWeekEndDate(),
                weekRecord.getTitle(),
                projectName == null || projectName.isBlank() ? "unspecified" : projectName,
                userPosition == null || userPosition.isBlank() ? "developer" : userPosition,
                fragmentLines);
    }
}
