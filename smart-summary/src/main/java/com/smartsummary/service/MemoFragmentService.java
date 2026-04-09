package com.smartsummary.service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.LambdaUpdateWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.repository.MemoFragmentRepository;
import com.smartsummary.repository.MemoWeekRecordRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class MemoFragmentService extends ServiceImpl<MemoFragmentRepository, MemoFragment> {

    private final MemoFragmentRepository memoFragmentRepository;
    private final MemoWeekRecordRepository memoWeekRecordRepository;

    public List<MemoFragment> listByWeekRecordId(Long userId, Long weekRecordId) {
        assertWeekOwnership(userId, weekRecordId);
        return memoFragmentRepository.findActiveByUserAndWeekRecord(userId, weekRecordId);
    }

    public MemoFragment createFragment(Long userId, Long weekRecordId, LocalDate workDate, String title, String content,
                                       String status, String priority, String tag, Integer sortOrder) {
        assertWeekOwnership(userId, weekRecordId);
        MemoFragment fragment = new MemoFragment();
        fragment.setUserId(userId);
        fragment.setWeekRecordId(weekRecordId);
        fragment.setWorkDate(workDate != null ? workDate : LocalDate.now());
        fragment.setTitle(title == null || title.isBlank() ? "Untitled Fragment" : title);
        fragment.setContent(content == null ? "" : content);
        fragment.setStatus(status == null || status.isBlank() ? "done" : status);
        fragment.setPriority(priority == null || priority.isBlank() ? "medium" : priority);
        fragment.setTag(tag);
        fragment.setSortOrder(sortOrder != null ? sortOrder : nextSortOrder(userId, weekRecordId));
        fragment.setCreatedAt(LocalDateTime.now());
        fragment.setUpdatedAt(LocalDateTime.now());
        save(fragment);
        return fragment;
    }

    public MemoFragment updateFragment(Long userId, Long id, Long weekRecordId, LocalDate workDate, String title,
                                       String content, String status, String priority, String tag, Integer sortOrder) {
        MemoFragment current = getOwnedFragment(userId, id);
        Long targetWeekId = weekRecordId != null ? weekRecordId : current.getWeekRecordId();
        assertWeekOwnership(userId, targetWeekId);

        if (weekRecordId != null) current.setWeekRecordId(weekRecordId);
        if (workDate != null) current.setWorkDate(workDate);
        if (title != null) current.setTitle(title);
        if (content != null) current.setContent(content);
        if (status != null) current.setStatus(status);
        if (priority != null) current.setPriority(priority);
        if (tag != null) current.setTag(tag);
        if (sortOrder != null) current.setSortOrder(sortOrder);
        current.setUpdatedAt(LocalDateTime.now());

        update(new LambdaUpdateWrapper<MemoFragment>()
                .eq(MemoFragment::getId, id)
                .eq(MemoFragment::getUserId, userId)
                .isNull(MemoFragment::getDeletedAt)
                .set(MemoFragment::getWeekRecordId, current.getWeekRecordId())
                .set(MemoFragment::getWorkDate, current.getWorkDate())
                .set(MemoFragment::getTitle, current.getTitle())
                .set(MemoFragment::getContent, current.getContent())
                .set(MemoFragment::getStatus, current.getStatus())
                .set(MemoFragment::getPriority, current.getPriority())
                .set(MemoFragment::getTag, current.getTag())
                .set(MemoFragment::getSortOrder, current.getSortOrder())
                .set(MemoFragment::getUpdatedAt, current.getUpdatedAt()));
        return getOwnedFragment(userId, id);
    }

    public void deleteFragment(Long userId, Long id) {
        if (!update(new LambdaUpdateWrapper<MemoFragment>()
                .eq(MemoFragment::getId, id)
                .eq(MemoFragment::getUserId, userId)
                .isNull(MemoFragment::getDeletedAt)
                .set(MemoFragment::getDeletedAt, LocalDateTime.now())
                .set(MemoFragment::getUpdatedAt, LocalDateTime.now()))) {
            throw new RuntimeException("Fragment not found");
        }
    }

    @Transactional
    public void batchUpdateSort(Long userId, Long weekRecordId, List<Long> orderedIds) {
        assertWeekOwnership(userId, weekRecordId);
        if (orderedIds == null || orderedIds.isEmpty()) {
            return;
        }
        int order = 1;
        for (Long id : orderedIds) {
            update(new LambdaUpdateWrapper<MemoFragment>()
                    .eq(MemoFragment::getId, id)
                    .eq(MemoFragment::getUserId, userId)
                    .eq(MemoFragment::getWeekRecordId, weekRecordId)
                    .isNull(MemoFragment::getDeletedAt)
                    .set(MemoFragment::getSortOrder, order++)
                    .set(MemoFragment::getUpdatedAt, LocalDateTime.now()));
        }
    }

    public void softDeleteByWeekRecord(Long userId, Long weekRecordId) {
        update(new LambdaUpdateWrapper<MemoFragment>()
                .eq(MemoFragment::getUserId, userId)
                .eq(MemoFragment::getWeekRecordId, weekRecordId)
                .isNull(MemoFragment::getDeletedAt)
                .set(MemoFragment::getDeletedAt, LocalDateTime.now())
                .set(MemoFragment::getUpdatedAt, LocalDateTime.now()));
    }

    private MemoFragment getOwnedFragment(Long userId, Long id) {
        MemoFragment fragment = getOne(new LambdaQueryWrapper<MemoFragment>()
                .eq(MemoFragment::getId, id)
                .eq(MemoFragment::getUserId, userId)
                .isNull(MemoFragment::getDeletedAt));
        if (fragment == null) {
            throw new RuntimeException("Fragment not found");
        }
        return fragment;
    }

    private void assertWeekOwnership(Long userId, Long weekRecordId) {
        MemoWeekRecord weekRecord = memoWeekRecordRepository.selectOne(new LambdaQueryWrapper<MemoWeekRecord>()
                .eq(MemoWeekRecord::getId, weekRecordId)
                .eq(MemoWeekRecord::getUserId, userId)
                .isNull(MemoWeekRecord::getDeletedAt));
        if (weekRecord == null) {
            throw new RuntimeException("Week record not found");
        }
    }

    private Integer nextSortOrder(Long userId, Long weekRecordId) {
        MemoFragment last = getOne(new LambdaQueryWrapper<MemoFragment>()
                .eq(MemoFragment::getUserId, userId)
                .eq(MemoFragment::getWeekRecordId, weekRecordId)
                .isNull(MemoFragment::getDeletedAt)
                .orderByDesc(MemoFragment::getSortOrder)
                .last("LIMIT 1"));
        return last == null || last.getSortOrder() == null ? 1 : last.getSortOrder() + 1;
    }
}
