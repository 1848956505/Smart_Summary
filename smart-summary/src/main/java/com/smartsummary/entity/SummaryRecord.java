package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.FieldFill;
import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableField;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@TableName("summary_records")
public class SummaryRecord {
    @TableId(type = IdType.AUTO)
    private Long id;

    private Long userId;

    private Long sourceWeekRecordId;

    private String originalText;

    private String summaryText;

    private String style;  // table/list

    private String modelId;

    private String apiKey;

    private String baseUrl;

    private Double temperature;
    private Integer maxTokens;

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}
