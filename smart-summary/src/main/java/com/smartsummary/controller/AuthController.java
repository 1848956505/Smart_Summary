package com.smartsummary.controller;

import com.smartsummary.entity.User;
import com.smartsummary.service.UserService;
import lombok.Data;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AuthController {

    private final UserService userService;

    @PostMapping("/register")
    public Map<String, Object> register(@RequestBody AuthRequest request) {
        try {
            User user = userService.register(request.getUsername(), request.getPassword(), request.getEmail());
            Map<String, Object> data = new HashMap<>();
            data.put("id", user.getId());
            data.put("username", user.getUsername());
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", data);
            return result;
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("message", e.getMessage() != null ? e.getMessage() : "注册失败");
            return result;
        }
    }

    @PostMapping("/login")
    public Map<String, Object> login(@RequestBody AuthRequest request) {
        try {
            User user = userService.login(request.getUsername(), request.getPassword());
            Map<String, Object> data = new HashMap<>();
            data.put("id", user.getId());
            data.put("username", user.getUsername());
            Map<String, Object> result = new HashMap<>();
            result.put("success", true);
            result.put("data", data);
            return result;
        } catch (Exception e) {
            Map<String, Object> result = new HashMap<>();
            result.put("success", false);
            result.put("message", e.getMessage() != null ? e.getMessage() : "登录失败");
            return result;
        }
    }

    @Data
    public static class AuthRequest {
        private String username;
        private String password;
        private String email;
    }
}