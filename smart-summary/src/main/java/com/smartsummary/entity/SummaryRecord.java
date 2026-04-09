package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.*;
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

    private String style;  // 钉钉/飞书/企微

    private String modelId;    // 模型名称

    private String apiKey;     // API密钥

    private String baseUrl;   // 接口地址

    private Double temperature; // 生成随机性

    private Integer maxTokens;  // 最大长度

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}
