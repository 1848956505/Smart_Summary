package com.smartsummary.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smartsummary.entity.MemoFragment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface MemoFragmentRepository extends BaseMapper<MemoFragment> {

    @Select("""
            SELECT *
            FROM memo_fragments
            WHERE user_id = #{userId}
              AND week_record_id = #{weekRecordId}
              AND deleted_at IS NULL
            ORDER BY work_date ASC, sort_order ASC, created_at ASC
            """)
    List<MemoFragment> findActiveByUserAndWeekRecord(@Param("userId") Long userId, @Param("weekRecordId") Long weekRecordId);
}
