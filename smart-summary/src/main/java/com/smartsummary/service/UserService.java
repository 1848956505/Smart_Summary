package com.smartsummary.service;

import com.smartsummary.entity.User;
import com.smartsummary.repository.UserRepository;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class UserService extends ServiceImpl<UserRepository, User> {

    private final PasswordEncoder passwordEncoder;

    public User register(String username, String password, String email) {
        // 检查用户名是否已存在
        if (count(new LambdaQueryWrapper<User>().eq(User::getUsername, username)) > 0) {
            throw new RuntimeException("用户名已存在");
        }

        User user = new User();
        user.setUsername(username);
        user.setPassword(passwordEncoder.encode(password));
        user.setEmail(email);
        // 设置默认值
        user.setModelId("qwen2.5-7b-instruct");
        user.setBaseUrl("http://localhost:8000");
        user.setTemperature(0.7);
        user.setMaxTokens(2048);
        save(user);
        return user;
    }

    public User login(String username, String password) {
        User user = getOne(new LambdaQueryWrapper<User>().eq(User::getUsername, username));
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        if (!passwordEncoder.matches(password, user.getPassword())) {
            throw new RuntimeException("密码错误");
        }
        return user;
    }
    
    // 更新用户信息
    public boolean updateUserInfo(Map<String, Object> params) {
        // 处理 userId，可能是 Integer 或 Long
        Object userIdObj = params.get("userId");
        Long userId;
        if (userIdObj instanceof Long) {
            userId = (Long) userIdObj;
        } else if (userIdObj instanceof Integer) {
            userId = ((Integer) userIdObj).longValue();
        } else if (userIdObj instanceof Number) {
            userId = ((Number) userIdObj).longValue();
        } else {
            throw new RuntimeException("无效的用户ID");
        }
        
        User user = getById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        
        if (params.containsKey("username") && params.get("username") != null) {
            user.setUsername((String) params.get("username"));
        }
        if (params.containsKey("email") && params.get("email") != null) {
            user.setEmail((String) params.get("email"));
        }
        if (params.containsKey("avatar") && params.get("avatar") != null) {
            user.setAvatar((String) params.get("avatar"));
        }
        if (params.containsKey("position") && params.get("position") != null) {
            user.setPosition((String) params.get("position"));
        }
        if (params.containsKey("modelId") && params.get("modelId") != null) {
            user.setModelId((String) params.get("modelId"));
        }
        if (params.containsKey("apiKey") && params.get("apiKey") != null) {
            user.setApiKey((String) params.get("apiKey"));
        }
        if (params.containsKey("baseUrl") && params.get("baseUrl") != null) {
            user.setBaseUrl((String) params.get("baseUrl"));
        }
        if (params.containsKey("temperature") && params.get("temperature") != null) {
            user.setTemperature((Double) params.get("temperature"));
        }
        if (params.containsKey("maxTokens") && params.get("maxTokens") != null) {
            Object maxTokensObj = params.get("maxTokens");
            if (maxTokensObj instanceof Integer) {
                user.setMaxTokens((Integer) maxTokensObj);
            } else if (maxTokensObj instanceof Long) {
                user.setMaxTokens(((Long) maxTokensObj).intValue());
            } else if (maxTokensObj instanceof Number) {
                user.setMaxTokens(((Number) maxTokensObj).intValue());
            }
        }
        
        return updateById(user);
    }
    
    // 修改密码
    public boolean changePassword(Long userId, String oldPassword, String newPassword) {
        User user = getById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        if (!passwordEncoder.matches(oldPassword, user.getPassword())) {
            throw new RuntimeException("原密码错误");
        }
        user.setPassword(passwordEncoder.encode(newPassword));
        return updateById(user);
    }
    
    // 获取用户信息（不返回密码）
    public Map<String, Object> getUserInfo(Long userId) {
        User user = getById(userId);
        if (user == null) {
            throw new RuntimeException("用户不存在");
        }
        return Map.of(
            "id", user.getId(),
            "username", user.getUsername() != null ? user.getUsername() : "",
            "email", user.getEmail() != null ? user.getEmail() : "",
            "avatar", user.getAvatar() != null ? user.getAvatar() : "",
            "position", user.getPosition() != null ? user.getPosition() : "",
            "modelId", user.getModelId() != null ? user.getModelId() : "qwen2.5-7b-instruct",
            "apiKey", user.getApiKey() != null ? user.getApiKey() : "",
            "baseUrl", user.getBaseUrl() != null ? user.getBaseUrl() : "http://localhost:8000",
            "temperature", user.getTemperature() != null ? user.getTemperature() : 0.7,
            "maxTokens", user.getMaxTokens() != null ? user.getMaxTokens() : 2048
        );
    }
}