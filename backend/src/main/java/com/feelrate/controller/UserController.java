package com.feelrate.controller;

import com.feelrate.domain.User;
import com.feelrate.config.TokenProvider;
import com.feelrate.service.UserService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequiredArgsConstructor
@RequestMapping("/users")
public class UserController {
    private final UserService userService;
    private final TokenProvider tokenProvider;

    @GetMapping("/me")
    public ResponseEntity<?> getCurrentUser(@RequestHeader("Authorization") String authHeader) {
        String token = authHeader.replace("Bearer ", "");
        Long userId = tokenProvider.getUserId(token);

        if (userId == null) {
            return ResponseEntity.status(401).body("유효하지 않은 토큰입니다.");
        }

        User user = userService.findById(userId);

        return ResponseEntity.ok(Map.of(
                "id", user.getId(),
                "name", user.getName(),
                "email", user.getEmail()
        ));
    }
}
