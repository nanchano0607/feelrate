package com.feelrate.controller;


import com.feelrate.domain.Menu;
import com.feelrate.domain.Restaurant;
import com.feelrate.dto.FilterRequestDto;
import com.feelrate.dto.MenuDto;
import com.feelrate.service.MenuService;
import com.feelrate.service.RestaurantService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/restaurants")
public class MenuController {
    private final MenuService menuService;
    private final RestaurantService restaurantService;

    @PostMapping("{placeId}/menus")
    public ResponseEntity<?> saveRestaurantMenus(@PathVariable("placeId") Integer placeId, @RequestBody List<Menu> menus){
        menuService.saveMenus(placeId, menus);
        return ResponseEntity.ok().build();
    }

    @GetMapping("{placeId}/menus")
    public ResponseEntity<List<MenuDto>> getRestaurantMenus(@PathVariable("placeId") Integer placeId){
        List<Menu> menus = menuService.getMenusByPlaceId(placeId);
        List<MenuDto> menuDtos = menus.stream()
                .map(menu -> new MenuDto(menu.getName(), menu.getPrice()))
                .collect(Collectors.toList());
        return ResponseEntity.ok(menuDtos);

    }

    @PostMapping("/filter/menu")
    public ResponseEntity<List<Integer>> getMenuFilter(@RequestBody FilterRequestDto requestDto) {
        // 키워드에 해당하는 placeId 식당들을 메뉴 기준으로 조회
        List<Integer> matchedIdsByMenu = menuService.findByMenu(requestDto.getKeywords());

        // 키워드에 해당하는 placeId 식당들을 카테고리 기준으로 조회
        List<Integer> matchedIdsByCategory = restaurantService.findByCategory(requestDto.getKeywords());

        // placeId들을 합치고 중복 제거
        Set<Integer> totalMatchedIds = new HashSet<>();
        totalMatchedIds.addAll(matchedIdsByMenu);
        totalMatchedIds.addAll(matchedIdsByCategory);

        return ResponseEntity.ok(new ArrayList<>(totalMatchedIds));
    }

    @PostMapping("/filter/context")
    public ResponseEntity<List<Integer>> getContextFilter(@RequestBody FilterRequestDto requestDto) {
        List<Integer> matchedIdsByContext = restaurantService.findByContext(requestDto.getKeywords());
        return ResponseEntity.ok(matchedIdsByContext);
    }
}
