package com.feelrate.controller;

import com.feelrate.dto.CreateAccessTokenRequest;
import com.feelrate.dto.CreateAccessTokenResponse;
import com.feelrate.repository.RefreshTokenRepository;
import com.feelrate.service.TokenService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RequiredArgsConstructor
@RestController
public class TokenApiController {
    private final TokenService tokenService;
    private final RefreshTokenRepository refreshTokenRepository;

//    @PostMapping("/api/token")
//    public ResponseEntity<CreateAccessTokenResponse> createAccessToken(@RequestBody CreateAccessTokenRequest request){
//        String newAccessToken=tokenService.createdNewAccessToken(request.getRefreshToken());
//        return ResponseEntity.status(HttpStatus.CREATED).body(new CreateAccessTokenResponse(newAccessToken));
//    }
@PostMapping("/api/token")
public ResponseEntity<CreateAccessTokenResponse> createAccessToken(@RequestBody Map<String, Long> request) {
    Long userId = request.get("user_id");
    String refreshToken = refreshTokenRepository.findByUserId(userId)
            .orElseThrow(() -> new IllegalArgumentException("Refresh token not found"))
            .getRefreshToken();

    String newAccessToken = tokenService.createdNewAccessToken(refreshToken);
    return ResponseEntity.status(HttpStatus.CREATED).body(new CreateAccessTokenResponse(newAccessToken));
}
}
