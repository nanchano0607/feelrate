package com.feelrate.service;

import com.feelrate.domain.Menu;
import com.feelrate.domain.Restaurant;
import com.feelrate.repository.MenuRepository;
import com.feelrate.repository.RestaurantRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.*;

@Service
@RequiredArgsConstructor
public class MenuService {

    private final MenuRepository menuRepository;
    private final RestaurantRepository restaurantRepository;

    public List<Menu> getMenusByPlaceId(Integer placeId) {
        return menuRepository.findByRestaurant_PlaceId(placeId);
    }

    public void saveMenus(Integer placeId, List<Menu> menus) {
        Restaurant restaurant = restaurantRepository.findById(placeId)
                .orElseThrow(() -> new IllegalArgumentException("식당이 존재하지 않음"));

        for (Menu menu : menus) {
            menu.setRestaurant(restaurant);
        }

        menuRepository.saveAll(menus);
    }

    public List<Integer> findByMenu(List<String> keywords) {
        if (keywords == null || keywords.isEmpty()) {
            return Collections.emptyList(); // 또는 예외를 던져도 됨
        }

        Set<Integer> matchedPlaceIds = new HashSet<>();

        for (String keyword : keywords) {
            List<Integer> ids = menuRepository.findRestaurantIdsByMenuKeyword(keyword);
            matchedPlaceIds.addAll(ids);
        }

        return new ArrayList<>(matchedPlaceIds);
    }
}
