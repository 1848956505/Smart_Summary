package com.smartsummary.repository;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.smartsummary.entity.SummaryRecord;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface SummaryRecordRepository extends BaseMapper<SummaryRecord> {
}