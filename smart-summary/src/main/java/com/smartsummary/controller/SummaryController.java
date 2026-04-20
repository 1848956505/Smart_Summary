package com.smartsummary.controller;

import com.smartsummary.entity.SummaryRecord;
import com.smartsummary.entity.User;
import com.smartsummary.service.LlmService;
import com.smartsummary.service.SummaryRecordService;
import com.smartsummary.service.UserService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

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

    @PostMapping("/generate")
    public Map<String, Object> generate(@RequestBody GenerateRequest request) {
        try {
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

            String normalizedStyle = llmService.normalizeStyle(request.getStyle());
            String summary = llmService.generateSummary(request.getText(), normalizedStyle, userConfig);

            if (request.getUserId() != null) {
                SummaryRecord record = new SummaryRecord();
                record.setUserId(request.getUserId());
                record.setOriginalText(request.getText());
                record.setSummaryText(summary);
                record.setStyle(normalizedStyle);
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

    @GetMapping("/history")
    public Map<String, Object> getHistory(@RequestParam Long userId) {
        try {
            List<SummaryRecord> records = summaryRecordService.getUserHistory(userId);
            records.forEach(record -> record.setApiKey("***"));
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", records);
            return result;
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    @GetMapping("/history/{id}")
    public Map<String, Object> getHistoryDetail(@PathVariable Long id) {
        try {
            SummaryRecord record = summaryRecordService.getRecordById(id);
            if (record == null) {
                return Map.of("success", false, "message", "记录不存在");
            }
            record.setApiKey("***");
            return Map.of("success", true, "data", record);
        } catch (Exception e) {
            return Map.of("success", false, "message", e.getMessage());
        }
    }

    @DeleteMapping("/history/{id}")
    public Map<String, Object> deleteHistory(@PathVariable Long id) {
        try {
            boolean success = summaryRecordService.deleteRecord(id);
            if (success) {
                return Map.of("success", true, "message", "删除成功");
            }
            return Map.of("success", false, "message", "删除失败");
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
