package com.smartsummary.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smartsummary.entity.MemoFolder;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface MemoFolderRepository extends BaseMapper<MemoFolder> {

    @Select("""
            SELECT *
            FROM memo_folders
            WHERE user_id = #{userId}
              AND deleted_at IS NULL
            ORDER BY sort_order ASC, created_at ASC
            """)
    List<MemoFolder> findActiveByUserId(@Param("userId") Long userId);
}
