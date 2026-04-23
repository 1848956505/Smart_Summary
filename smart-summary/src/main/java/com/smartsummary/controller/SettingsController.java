package com.smartsummary.controller;

import com.smartsummary.service.UserService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/settings")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class SettingsController {

    private final UserService userService;

    // 获取用户设置
    @GetMapping
    public Map<String, Object> getSettings(@RequestParam Long userId) {
        try {
            Map<String, Object> data = userService.getUserInfo(userId);
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", data);
            return result;
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("message", e.getMessage());
            return result;
        }
    }

    // 更新用户信息
    @PutMapping("/info")
    public Map<String, Object> updateInfo(@RequestBody Map<String, Object> params) {
        try {
            boolean success = userService.updateUserInfo(params);
            Map<String, Object> result = new HashMap<>();
            result.put("success", success);
            if (success) {
                result.put("message", "更新成功");
            } else {
                result.put("message", "更新失败");
            }
            return result;
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("message", e.getMessage());
            return result;
        }
    }

    // 修改密码
    @PutMapping("/password")
    public Map<String, Object> changePassword(@RequestBody ChangePasswordRequest request) {
        try {
            boolean success = userService.changePassword(request.getUserId(), request.getOldPassword(), request.getNewPassword());
            Map<String, Object> result = new HashMap<>();
            result.put("success", success);
            if (success) {
                result.put("message", "密码修改成功");
            } else {
                result.put("message", "密码修改失败");
            }
            return result;
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("message", e.getMessage());
            return result;
        }
    }

    // 测试模型连接
    @PostMapping("/test-connection")
    public Map<String, Object> testConnection(@RequestBody TestConnectionRequest request) {
        Map<String, Object> result = new HashMap<>();
        try {
            long startedAt = System.currentTimeMillis();
            // 创建 HTTP 客户端
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                    .build();

            // 构建简单的 models API 请求来测试连接
            String url = request.getBaseUrl() + "/v1/models";
            
            Request httpRequest = new Request.Builder()
                    .url(url)
                    .addHeader("Authorization", "Bearer " + request.getApiKey())
                    .get()
                    .build();

            try (Response response = client.newCall(httpRequest).execute()) {
                long latencyMs = System.currentTimeMillis() - startedAt;
                if (response.isSuccessful()) {
                    result.put("success", true);
                    result.put("message", "连接成功！模型服务正常运行。");
                    result.put("status", "normal");
                    result.put("latencyMs", latencyMs);
                } else {
                    result.put("success", false);
                    result.put("message", "连接失败: HTTP " + response.code() + " " + response.message());
                    result.put("status", "error");
                    result.put("latencyMs", latencyMs);
                }
            }
            return result;
        } catch (Exception e) {
            result.put("success", false);
            result.put("message", "连接失败: " + e.getMessage());
            result.put("status", "error");
            return result;
        }
    }

    @Data
    public static class ChangePasswordRequest {
        private Long userId;
        private String oldPassword;
        private String newPassword;
    }

    @Data
    public static class TestConnectionRequest {
        private String baseUrl;
        private String apiKey;
        private String modelId;
    }
}
