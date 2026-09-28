package com.feelrate.service;
import com.feelrate.domain.User;
import com.feelrate.dto.UserProfile;
import com.feelrate.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.oauth2.client.userinfo.DefaultOAuth2UserService;
import org.springframework.security.oauth2.client.userinfo.OAuth2UserRequest;
import org.springframework.security.oauth2.core.OAuth2AuthenticationException;
import org.springframework.security.oauth2.core.user.OAuth2User;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class OAuth2UserCustomService extends DefaultOAuth2UserService {

    private final UserRepository userRepository;

    @Override
    public OAuth2User loadUser(OAuth2UserRequest userRequest) throws OAuth2AuthenticationException {
        OAuth2User user = super.loadUser(userRequest); // ❶ 요청을 바탕으로 유저 정보를 담은 객체 반환
        saveOrUpdate(user);

        return user;
    }

    // ❷ 유저가 있으면 업데이트, 없으면 유저 생성
    private User saveOrUpdate(OAuth2User oAuth2User) {
        UserProfile profile = new UserProfile(oAuth2User.getAttributes()); // ✅ DTO 사용

        User user = userRepository.findByEmail(profile.getEmail())
                .map(entity -> entity.update(profile.getName()))
                .orElse(User.builder()
                        .email(profile.getEmail())
                        .name(profile.getName())
                        .build());

        return userRepository.save(user);
    }
}
