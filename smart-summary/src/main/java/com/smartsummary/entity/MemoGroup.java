package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * @deprecated Archived compatibility model for memo_group_legacy.
 * Runtime chain must not depend on this model.
 */
@Deprecated
@Data
@TableName("memo_group_legacy")
public class MemoGroup {

    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private String title;

    private String folderName;

    private LocalDate weekStartDate;

    private LocalDate weekEndDate;

    private String weekDate;

    private Integer sortOrder;

    private LocalDateTime createTime;

    private LocalDateTime updateTime;

    private Integer deleted;
}
