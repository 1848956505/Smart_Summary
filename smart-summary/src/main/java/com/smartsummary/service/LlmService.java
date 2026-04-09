package com.smartsummary.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.*;

@Slf4j
@Service
@RequiredArgsConstructor
public class LlmService {

    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");
    private static final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(120, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(60, java.util.concurrent.TimeUnit.SECONDS)
            .build();

    /**
     * 生成工作总结（通用）
     */
    public String generateSummary(String userInput, String style, UserConfig userConfig) throws IOException {
        String prompt = buildPrompt(userInput, style);

        log.info("LLM call baseUrl={}, model={}, style={}", userConfig.getBaseUrl(), userConfig.getModelId(), style);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", userConfig.getModelId());
        requestBody.put("messages", Arrays.asList(
                Map.of("role", "system", "content", "你是一个专业的工作总结生成助手。"),
                Map.of("role", "user", "content", prompt)
        ));
        requestBody.put("temperature", userConfig.getTemperature());
        requestBody.put("max_tokens", userConfig.getMaxTokens());

        return executeChat(requestBody, userConfig);
    }

    /**
     * 生成碎片周报（结构化）
     */
    public String generateWeeklySummary(String userInput, UserConfig userConfig) throws IOException {
        String prompt = """
                你将收到一周的工作碎片记录，请整理成专业周报。
                输出必须包含以下结构：
                1. 本周工作概述
                2. 已完成工作
                3. 问题与处理
                4. 阶段成果
                5. 下周计划

                要求：
                - 不得编造未出现的事实；
                - 语言正式、精炼、可汇报；
                - 对零散表述进行适度专业化改写；
                - 优先保留关键事项、结果和处理动作。

                输入：
                """ + userInput;

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", userConfig.getModelId());
        requestBody.put("messages", Arrays.asList(
                Map.of("role", "system", "content", "你是专业的研发工作总结助手。"),
                Map.of("role", "user", "content", prompt)
        ));
        requestBody.put("temperature", userConfig.getTemperature());
        requestBody.put("max_tokens", userConfig.getMaxTokens());

        return executeChat(requestBody, userConfig);
    }

    private String executeChat(Map<String, Object> requestBody, UserConfig userConfig) throws IOException {
        String json = objectMapper.writeValueAsString(requestBody);

        Request request = new Request.Builder()
                .url(getChatCompletionsUrl(userConfig.getBaseUrl()))
                .addHeader("Authorization", "Bearer " + userConfig.getApiKey())
                .addHeader("Content-Type", "application/json")
                .post(RequestBody.create(json, JSON))
                .build();

        try (Response response = client.newCall(request).execute()) {
            String responseBody = Objects.requireNonNull(response.body()).string();
            if (!response.isSuccessful()) {
                throw new IOException("调用大模型失败: HTTP " + response.code() + " - " + responseBody);
            }

            JsonNode root = objectMapper.readTree(responseBody);
            if (root.has("error")) {
                String errorMsg = root.path("error").path("message").asText("未知错误");
                throw new IOException("API返回错误: " + errorMsg);
            }

            JsonNode content = root.path("choices").path(0).path("message").path("content");
            if (content.isMissingNode() || content.isNull()) {
                throw new IOException("API响应缺少content字段");
            }
            return content.asText();
        }
    }

    private String buildPrompt(String userInput, String style) {
        String styleDesc = switch (style.toLowerCase()) {
            case "dingtalk", "钉钉" -> "钉钉风格：简洁正式，适度使用分点。";
            case "feishu", "飞书" -> "飞书风格：结构清晰，强调层次。";
            case "wechat", "企微", "wechatwork" -> "企业微信风格：正式规范，适合汇报。";
            default -> "默认风格：正式专业，结构清晰。";
        };

        return String.format("""
                请将以下工作记录转化为专业的工作总结。
                风格要求：%s

                工作记录：
                %s

                请直接输出总结正文。
                """, styleDesc, userInput);
    }

    private String getChatCompletionsUrl(String baseUrl) {
        if (baseUrl == null || baseUrl.trim().isEmpty()) {
            baseUrl = "http://localhost:8000";
        }
        baseUrl = baseUrl.trim();
        if (baseUrl.endsWith("/")) {
            baseUrl = baseUrl.substring(0, baseUrl.length() - 1);
        }
        return baseUrl + "/v1/chat/completions";
    }

    @Data
    public static class UserConfig {
        private String baseUrl;
        private String modelId;
        private String apiKey;
        private Double temperature;
        private Integer maxTokens;

        public String getBaseUrl() {
            return (baseUrl == null || baseUrl.trim().isEmpty()) ? "http://localhost:8000" : baseUrl.trim();
        }

        public String getModelId() {
            return modelId != null ? modelId.trim() : "qwen2.5-7b-instruct";
        }

        public String getApiKey() {
            return (apiKey == null || apiKey.isBlank()) ? "lm-studio" : apiKey;
        }

        public Double getTemperature() {
            return temperature != null ? temperature : 0.7;
        }

        public Integer getMaxTokens() {
            return maxTokens != null ? maxTokens : 2048;
        }
    }
}
