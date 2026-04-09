package com.smartsummary.controller;

import com.smartsummary.entity.MemoFolder;
import com.smartsummary.entity.MemoFragment;
import com.smartsummary.entity.MemoWeekRecord;
import com.smartsummary.service.CurrentUserService;
import com.smartsummary.service.MemoFolderService;
import com.smartsummary.service.MemoFragmentService;
import com.smartsummary.service.MemoWeekRecordService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class MemoControllerRegressionTest {

    @Mock
    private MemoFolderService memoFolderService;
    @Mock
    private MemoWeekRecordService memoWeekRecordService;
    @Mock
    private MemoFragmentService memoFragmentService;
    @Mock
    private CurrentUserService currentUserService;

    @InjectMocks
    private MemoController memoController;

    @BeforeEach
    void setUp() {
        when(currentUserService.requireCurrentUserId()).thenReturn(1L);
    }

    @Test
    void createFolder_shouldSucceed() {
        MemoController.FolderRequest request = new MemoController.FolderRequest();
        request.setName("研发事项");

        MemoFolder folder = new MemoFolder();
        folder.setId(101L);
        folder.setUserId(1L);
        folder.setName("研发事项");

        when(memoFolderService.createFolder(eq(1L), eq("研发事项"), isNull(), isNull())).thenReturn(folder);

        Map<String, Object> result = memoController.createFolder(request);

        assertEquals(Boolean.TRUE, result.get("success"));
        assertSame(folder, result.get("data"));
        verify(memoFolderService).createFolder(1L, "研发事项", null, null);
    }

    @Test
    void createWeekRecord_shouldSucceed() {
        MemoController.WeekRequest request = new MemoController.WeekRequest();
        request.setFolderId(101L);
        request.setTitle("2026W14");
        request.setWeekStartDate(LocalDate.of(2026, 4, 6));
        request.setWeekEndDate(LocalDate.of(2026, 4, 12));

        MemoWeekRecord week = new MemoWeekRecord();
        week.setId(201L);
        week.setUserId(1L);
        week.setFolderId(101L);
        week.setTitle("2026W14");

        when(memoWeekRecordService.createWeekRecord(1L, 101L, "2026W14",
                LocalDate.of(2026, 4, 6), LocalDate.of(2026, 4, 12))).thenReturn(week);

        Map<String, Object> result = memoController.createWeek(request);

        assertEquals(Boolean.TRUE, result.get("success"));
        assertSame(week, result.get("data"));
        verify(memoWeekRecordService).createWeekRecord(1L, 101L, "2026W14",
                LocalDate.of(2026, 4, 6), LocalDate.of(2026, 4, 12));
    }

    @Test
    void createFragment_shouldSucceed() {
        MemoController.FragmentRequest request = new MemoController.FragmentRequest();
        request.setWeekRecordId(201L);
        request.setWorkDate(LocalDate.of(2026, 4, 7));
        request.setTitle("完成接口联调");
        request.setContent("对接 memo weeks/fragments");
        request.setStatus("done");
        request.setPriority("medium");
        request.setTag("开发");
        request.setSortOrder(1);

        MemoFragment fragment = new MemoFragment();
        fragment.setId(301L);
        fragment.setWeekRecordId(201L);

        when(memoFragmentService.createFragment(1L, 201L, LocalDate.of(2026, 4, 7),
                "完成接口联调", "对接 memo weeks/fragments", "done", "medium", "开发", 1)).thenReturn(fragment);

        Map<String, Object> result = memoController.createFragment(request);

        assertEquals(Boolean.TRUE, result.get("success"));
        assertSame(fragment, result.get("data"));
        verify(memoFragmentService).createFragment(1L, 201L, LocalDate.of(2026, 4, 7),
                "完成接口联调", "对接 memo weeks/fragments", "done", "medium", "开发", 1);
    }

    @Test
    void listFragmentsByWeek_shouldSucceed() {
        MemoFragment one = fragment(1L, "todo", "开发");
        MemoFragment two = fragment(2L, "done", "测试");
        when(memoFragmentService.listByWeekRecordId(1L, 201L)).thenReturn(List.of(one, two));

        Map<String, Object> result = memoController.listFragments(201L, null);

        assertEquals(Boolean.TRUE, result.get("success"));
        List<?> data = (List<?>) result.get("data");
        assertEquals(2, data.size());
        verify(memoFragmentService).listByWeekRecordId(1L, 201L);
    }

    @Test
    void generateWeeklySummary_shouldSucceed() {
        MemoController.GenerateSummaryRequest request = new MemoController.GenerateSummaryRequest();
        request.setProjectName("Smart Summary");
        request.setUserPosition("后端开发");

        when(memoWeekRecordService.generateWeeklySummary(1L, 201L, "Smart Summary", "后端开发"))
                .thenReturn("本周总结内容");
        when(memoFragmentService.listByWeekRecordId(1L, 201L)).thenReturn(List.of(
                fragment(1L, "done", "开发"),
                fragment(2L, "doing", "调试")
        ));

        Map<String, Object> result = memoController.generateSummary(201L, request);

        assertEquals(Boolean.TRUE, result.get("success"));
        Map<String, Object> data = castMap(result.get("data"));
        assertEquals(201L, data.get("weekRecordId"));
        assertEquals("本周总结内容", data.get("summary"));
        Map<String, Object> stats = castMap(data.get("stats"));
        assertEquals(2L, stats.get("total"));
        assertEquals(1L, stats.get("done"));
        assertEquals(1L, stats.get("doing"));
    }

    @Test
    void deleteWeekRecord_shouldCallSoftDeleteChain() {
        Map<String, Object> result = memoController.deleteWeek(201L);

        assertEquals(Boolean.TRUE, result.get("success"));
        verify(memoWeekRecordService).deleteWeekRecord(1L, 201L);
    }

    @Test
    void crossUserAccess_shouldBeRejected() {
        when(memoWeekRecordService.getWeekRecordDetail(1L, 999L))
                .thenThrow(new RuntimeException("Week record not found"));

        RuntimeException ex = assertThrows(RuntimeException.class, () -> memoController.getWeek(999L));
        assertTrue(ex.getMessage().contains("Week record"));
    }

    private MemoFragment fragment(Long id, String status, String tag) {
        MemoFragment fragment = new MemoFragment();
        fragment.setId(id);
        fragment.setWeekRecordId(201L);
        fragment.setStatus(status);
        fragment.setTag(tag);
        fragment.setWorkDate(LocalDate.of(2026, 4, 7));
        fragment.setSortOrder(id.intValue());
        return fragment;
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> castMap(Object obj) {
        return (Map<String, Object>) obj;
    }
}
