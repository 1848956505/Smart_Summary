package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("memo_fragments")
public class MemoFragment {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long weekRecordId;

    private LocalDate workDate;

    private String title;

    private String content;

    private String status;

    private String priority;

    private String tag;

    private Integer sortOrder;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private LocalDateTime deletedAt;
}
