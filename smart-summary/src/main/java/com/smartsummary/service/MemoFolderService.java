package com.smartsummary.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.smartsummary.entity.MemoFolder;
import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.repository.MemoFolderRepository;
import com.smartsummary.repository.MemoFragmentRepository;
import com.smartsummary.repository.MemoWeekRecordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MemoFolderService extends ServiceImpl<MemoFolderRepository, MemoFolder> {

    private final MemoFolderRepository memoFolderRepository;
    private final MemoWeekRecordRepository memoWeekRecordRepository;
    private final MemoFragmentRepository memoFragmentRepository;

    public List<MemoFolder> listByUserId(Long userId) {
        return memoFolderRepository.findActiveByUserId(userId);
    }

    public MemoFolder createFolder(Long userId, String name, Integer sortOrder, Integer isCollapsed) {
        MemoFolder folder = new MemoFolder();
        folder.setUserId(userId);
        folder.setName((name == null || name.isBlank()) ? "Untitled Folder" : name);
        folder.setSortOrder(sortOrder != null ? sortOrder : nextSortOrder(userId));
        folder.setIsCollapsed(isCollapsed != null ? isCollapsed : 0);
        folder.setCreatedAt(LocalDateTime.now());
        folder.setUpdatedAt(LocalDateTime.now());
        save(folder);
        return folder;
    }

    public MemoFolder renameFolder(Long userId, Long folderId, String name) {
        if (name == null || name.isBlank()) {
            throw new RuntimeException("Folder name cannot be empty");
        }
        if (!update(new LambdaUpdateWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)
                .set(MemoFolder::getName, name)
                .set(MemoFolder::getUpdatedAt, LocalDateTime.now()))) {
            throw new RuntimeException("Folder not found");
        }
        return getFolderDetail(userId, folderId);
    }

    public MemoFolder updateCollapsed(Long userId, Long folderId, Integer isCollapsed) {
        if (!update(new LambdaUpdateWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)
                .set(MemoFolder::getIsCollapsed, isCollapsed != null ? isCollapsed : 0)
                .set(MemoFolder::getUpdatedAt, LocalDateTime.now()))) {
            throw new RuntimeException("Folder not found");
        }
        return getFolderDetail(userId, folderId);
    }

    public MemoFolder updateSortOrder(Long userId, Long folderId, Integer sortOrder) {
        if (sortOrder == null) {
            throw new RuntimeException("Sort order cannot be null");
        }
        if (!update(new LambdaUpdateWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)
                .set(MemoFolder::getSortOrder, sortOrder)
                .set(MemoFolder::getUpdatedAt, LocalDateTime.now()))) {
            throw new RuntimeException("Folder not found");
        }
        return getFolderDetail(userId, folderId);
    }

    @Transactional
    public void deleteFolder(Long userId, Long folderId) {
        MemoFolder folder = getFolderDetail(userId, folderId);

        List<MemoWeekRecord> weeks = memoWeekRecordRepository.selectList(new LambdaQueryWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getUserId, userId)
                .eq(MemoWeekRecord::getFolderId, folder.getId())
                .isNull(MemoWeekRecord::getDeletedAt));

        LocalDateTime now = LocalDateTime.now();
        for (MemoWeekRecord week : weeks) {
            memoFragmentRepository.update(null, new LambdaUpdateWrapper<MemoFragment>()
                    .eq(MemoFragment::getUserId, userId)
                    .eq(MemoFragment::getWeekRecordId, week.getId())
                    .isNull(MemoFragment::getDeletedAt)
                    .set(MemoFragment::getDeletedAt, now)
                    .set(MemoFragment::getUpdatedAt, now));
        }

        memoWeekRecordRepository.update(null, new LambdaUpdateWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getUserId, userId)
                .eq(MemoWeekRecord::getFolderId, folder.getId())
                .isNull(MemoWeekRecord::getDeletedAt)
                .set(MemoWeekRecord::getDeletedAt, now)
                .set(MemoWeekRecord::getUpdatedAt, now));

        update(new LambdaUpdateWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)
                .set(MemoFolder::getDeletedAt, now)
                .set(MemoFolder::getUpdatedAt, now));
    }

    public MemoFolder getFolderDetail(Long userId, Long folderId) {
        MemoFolder folder = getOne(new LambdaQueryWrapper<MemoFolder>()
                .eq(MemoFolder::getId, folderId)
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt));
        if (folder == null) {
            throw new RuntimeException("Folder not found");
        }
        return folder;
    }

    private Integer nextSortOrder(Long userId) {
        MemoFolder last = getOne(new LambdaQueryWrapper<MemoFolder>()
                .eq(MemoFolder::getUserId, userId)
                .isNull(MemoFolder::getDeletedAt)
                .orderByDesc(MemoFolder::getSortOrder)
                .last("LIMIT 1"));
        return last == null || last.getSortOrder() == null ? 1 : last.getSortOrder() + 1;
    }
}
