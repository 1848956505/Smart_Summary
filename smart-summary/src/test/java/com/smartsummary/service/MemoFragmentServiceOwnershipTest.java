package com.smartsummary.service;

import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.repository.MemoFragmentRepository;
import com.smartsummary.repository.MemoWeekRecordRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MemoFragmentServiceOwnershipTest {

    @Mock
    private MemoFragmentRepository memoFragmentRepository;
    @Mock
    private MemoWeekRecordRepository memoWeekRecordRepository;

    @InjectMocks
    private MemoFragmentService memoFragmentService;

    @Test
    void listByWeekRecordId_shouldRejectCrossUserAccess() {
        when(memoWeekRecordRepository.selectOne(any())).thenReturn(null);

        RuntimeException ex = assertThrows(RuntimeException.class,
                () -> memoFragmentService.listByWeekRecordId(1L, 200L));

        assertTrue(ex.getMessage().contains("Week record"));
        verify(memoFragmentRepository, never()).findActiveByUserAndWeekRecord(anyLong(), anyLong());
    }

    @Test
    void listByWeekRecordId_shouldReturnDataForOwnedWeek() {
        MemoWeekRecord ownedWeek = new MemoWeekRecord();
        ownedWeek.setId(200L);
        ownedWeek.setUserId(1L);
        when(memoWeekRecordRepository.selectOne(any())).thenReturn(ownedWeek);

        MemoFragment fragment = new MemoFragment();
        fragment.setId(300L);
        fragment.setWeekRecordId(200L);
        fragment.setTitle("完成阶段六");
        fragment.setWorkDate(LocalDate.of(2026, 4, 7));
        when(memoFragmentRepository.findActiveByUserAndWeekRecord(1L, 200L)).thenReturn(List.of(fragment));

        List<MemoFragment> result = memoFragmentService.listByWeekRecordId(1L, 200L);

        assertEquals(1, result.size());
        assertEquals(300L, result.get(0).getId());
    }
}
