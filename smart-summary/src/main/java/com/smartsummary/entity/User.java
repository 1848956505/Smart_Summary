package com.smartsummary.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("users")
public class User {
    @TableId(type = IdType.AUTO)
    private Long id;

    private String username;

    private String password;

    private String email;
    
    private String avatar;      // 用户头像URL
    
    private String position;   // 用户岗位
    
    private String modelId;    // 模型名称
    
    private String apiKey;     // API密钥
    
    private String baseUrl;    // 接口地址
    
    private Double temperature; // 生成随机性 0.0-1.5
    
    private Integer maxTokens;  // 最大长度 512-4096

    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updateTime;

    @TableLogic
    private Integer deleted;
}