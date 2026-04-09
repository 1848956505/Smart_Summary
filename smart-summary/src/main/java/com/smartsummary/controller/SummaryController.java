package com.smartsummary.controller;

import com.smartsummary.entity.SummaryRecord;
import com.smartsummary.entity.User;
import com.smartsummary.service.LlmService;
import com.smartsummary.service.SummaryRecordService;
import com.smartsummary.service.UserService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class SummaryController {

    private final LlmService llmService;
    private final SummaryRecordService summaryRecordService;
    private final UserService userService;

    /**
     * 生成工作总结
     */
    @PostMapping("/generate")
    public Map<String, Object> generate(@RequestBody GenerateRequest request) {
        try {
            // 获取用户配置
            LlmService.UserConfig userConfig = new LlmService.UserConfig();
            if (request.getUserId() != null) {
                User user = userService.getById(request.getUserId());
                if (user != null) {
                    userConfig.setBaseUrl(user.getBaseUrl());
                    userConfig.setModelId(user.getModelId());
                    userConfig.setApiKey(user.getApiKey());
                    userConfig.setTemperature(user.getTemperature());
                    userConfig.setMaxTokens(user.getMaxTokens());
                }
            }

            // 调用大模型生成（使用用户配置）
            String summary = llmService.generateSummary(request.getText(), request.getStyle(), userConfig);

            // 保存记录（包含模型参数）
            if (request.getUserId() != null) {
                SummaryRecord record = new SummaryRecord();
                record.setUserId(request.getUserId());
                record.setOriginalText(request.getText());
                record.setSummaryText(summary);
                record.setStyle(request.getStyle());
                // 保存模型参数
                record.setModelId(userConfig.getModelId());
                record.setApiKey(userConfig.getApiKey());
                record.setBaseUrl(userConfig.getBaseUrl());
                record.setTemperature(userConfig.getTemperature());
                record.setMaxTokens(userConfig.getMaxTokens());
                summaryRecordService.save(record);
            }

            return Map.of("success", true, "data", summary);
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    /**
     * 获取历史记录列表
     */
    @GetMapping("/history")
    public Map<String, Object> getHistory(@RequestParam Long userId) {
        try {
            List<SummaryRecord> records = summaryRecordService.getUserHistory(userId);
            // 返回时隐藏敏感信息
            records.forEach(record -> {
                record.setApiKey("***");
            });
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", records);
            return result;
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    /**
     * 获取单条历史记录详情
     */
    @GetMapping("/history/{id}")
    public Map<String, Object> getHistoryDetail(@PathVariable Long id) {
        try {
            SummaryRecord record = summaryRecordService.getRecordById(id);
            if (record == null) {
                return Map.of("success", false, "message", "记录不存在");
            }
            // 隐藏敏感信息
            record.setApiKey("***");
            return Map.of("success", true, "data", record);
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    /**
     * 删除历史记录
     */
    @DeleteMapping("/history/{id}")
    public Map<String, Object> deleteHistory(@PathVariable Long id) {
        try {
            boolean success = summaryRecordService.deleteRecord(id);
            if (success) {
                return Map.of("success", true, "message", "删除成功");
            } else {
                return Map.of("success", false, "message", "删除失败");
            }
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    @Data
    public static class GenerateRequest {
        private String text;
        private String style;
        private Long userId;
    }
}
