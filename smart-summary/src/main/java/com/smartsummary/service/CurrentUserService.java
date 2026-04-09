package com.smartsummary.service;

import com.smartsummary.entity.User;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;

/**
 * Lightweight current-user resolver.
 * Current implementation reads user id from request header "X-User-Id".
 * This acts as login-state bridge before JWT/session integration.
 */
@Service
@RequiredArgsConstructor
public class CurrentUserService {

    private final UserService userService;

    public Long requireCurrentUserId() {
        ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attributes == null || attributes.getRequest() == null) {
            throw new RuntimeException("未获取到登录态");
        }

        String headerValue = attributes.getRequest().getHeader("X-User-Id");
        if (headerValue == null || headerValue.isBlank()) {
            throw new RuntimeException("未登录或登录态失效");
        }

        Long userId;
        try {
            userId = Long.parseLong(headerValue.trim());
        } catch (NumberFormatException ex) {
            throw new RuntimeException("登录态用户ID无效");
        }

        User user = userService.getById(userId);
        if (user == null) {
            throw new RuntimeException("登录用户不存在");
        }
        return userId;
    }
}
