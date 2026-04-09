package com.smartsummary.service;

import com.smartsummary.entity.SummaryRecord;
import com.smartsummary.repository.SummaryRecordRepository;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class SummaryRecordService extends ServiceImpl<SummaryRecordRepository, SummaryRecord> {

    // 获取用户历史记录
    public List<SummaryRecord> getUserHistory(Long userId) {
        return list(new LambdaQueryWrapper<SummaryRecord>()
                .eq(SummaryRecord::getUserId, userId)
                .orderByDesc(SummaryRecord::getCreateTime)
                .last("LIMIT 50"));
    }

    // 获取单条记录
    public SummaryRecord getRecordById(Long id) {
        return getById(id);
    }

    // 删除记录
    public boolean deleteRecord(Long id) {
        return removeById(id);
    }
}
