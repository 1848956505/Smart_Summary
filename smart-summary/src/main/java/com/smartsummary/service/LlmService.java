package com.smartsummary.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;

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

    public String generateSummary(String userInput, String style, UserConfig userConfig) throws IOException {
        String normalizedStyle = normalizeStyle(style);
        String prompt = buildPrompt(userInput, normalizedStyle);

        log.info("LLM call baseUrl={}, model={}, style={}", userConfig.getBaseUrl(), userConfig.getModelId(), normalizedStyle);

        Map<String, Object> requestBody = new HashMap<>();
        requestBody.put("model", userConfig.getModelId());
        requestBody.put("messages", Arrays.asList(
                Map.of("role", "system", "content", "你是一名专业的工作周报生成助手。"),
                Map.of("role", "user", "content", prompt)
        ));
        requestBody.put("temperature", userConfig.getTemperature());
        requestBody.put("max_tokens", userConfig.getMaxTokens());

        return executeChat(requestBody, userConfig);
    }

    public String generateWeeklySummary(String userInput, UserConfig userConfig) throws IOException {
        String prompt = """
                你将收到一周的工作碎片记录，请整理成专业周报。
                输出必须包含以下结构：
                1. 本周工作概览
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

    public String normalizeStyle(String style) {
        String value = style == null ? "" : style.trim().toLowerCase(Locale.ROOT);
        return switch (value) {
            case "table", "表格" -> "table";
            case "list", "列表" -> "list";
            case "dingtalk", "钉钉", "feishu", "飞书", "wechat", "wechatwork", "企微", "企业微信" -> "list";
            default -> "list";
        };
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
                throw new IOException("API 返回错误: " + errorMsg);
            }

            JsonNode content = root.path("choices").path(0).path("message").path("content");
            if (content.isMissingNode() || content.isNull()) {
                throw new IOException("API 响应缺少 content 字段");
            }
            return content.asText();
        }
    }

    private String buildPrompt(String userInput, String style) {
        String styleDesc = switch (style) {
            case "table" -> "表格风格：优先使用清晰的 Markdown 表格组织信息。能表格化的内容尽量表格化，列名简洁，重点突出结果、进展、问题和计划。";
            case "list" -> "列表风格：使用清晰的标题与分点列表组织内容，层级明确，便于直接汇报或复制到文档中。";
            default -> "列表风格：使用清晰的标题与分点列表组织内容，层级明确，便于直接汇报或复制到文档中。";
        };

        return String.format("""
                请将以下工作记录转化为专业、可直接汇报的周报内容。
                风格要求：%s

                工作记录：
                %s

                输出要求：
                - 不要编造未出现的事实；
                - 保留关键成果、进展、问题、协作事项与下一步计划；
                - 语言专业、清晰、克制；
                - 直接输出正文，不要附加解释。
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
