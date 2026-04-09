package com.smartsummary.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smartsummary.entity.MemoWeekRecord;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface MemoWeekRecordRepository extends BaseMapper<MemoWeekRecord> {

    @Select("""
            SELECT *
            FROM memo_week_records
            WHERE user_id = #{userId}
              AND folder_id = #{folderId}
              AND deleted_at IS NULL
            ORDER BY week_start_date DESC, created_at DESC
            """)
    List<MemoWeekRecord> findActiveByUserAndFolder(@Param("userId") Long userId, @Param("folderId") Long folderId);
}
