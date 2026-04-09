package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import com.baomidou.mybatisplus.annotation.Version;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("memo_week_records")
public class MemoWeekRecord {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long folderId;

    private String title;

    private LocalDate weekStartDate;

    private LocalDate weekEndDate;

    private String status;

    private String summaryContent;

    @Version
    private Integer version;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private LocalDateTime deletedAt;
}
