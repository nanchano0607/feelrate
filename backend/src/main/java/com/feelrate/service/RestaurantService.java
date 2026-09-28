package com.feelrate.service;

import com.feelrate.domain.Restaurant;
import com.feelrate.domain.Review;
import com.feelrate.dto.RatingAndCount;
import com.feelrate.dto.RestaurantResponseDto;
import com.feelrate.repository.RestaurantRepository;
import com.feelrate.repository.ReviewRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class RestaurantService {

    private final RestaurantRepository restaurantRepository;
    private final ReviewRepository reviewRepository;

    // 저장 (중복 placeId 무시)
    @Transactional
    public Restaurant save(Restaurant restaurant) {
        if (restaurant.getPlaceId() == null) {
            throw new IllegalArgumentException("placeId가 null입니다.");
        }

        if (restaurantRepository.existsById(restaurant.getPlaceId())) {
            return restaurantRepository.findById(restaurant.getPlaceId()).orElse(null);
        }
        return restaurantRepository.save(restaurant);
    }


    public Optional<Restaurant> findByPlaceId(Integer placeId) {
        return restaurantRepository.findById(placeId);
    }

    public List<RatingAndCount> findByPlaceIdsRatingAndCount(List<Integer> placeIds) {
        List<Restaurant> restaurants = restaurantRepository.findAllById(placeIds);
        return restaurants.stream()
                .map(r -> new RatingAndCount(r.getPlaceId(), r.getRating(), r.getReviewCount()))
                .collect(Collectors.toList());
    }
    public List<Restaurant> findByPlaceIds(List<Integer> placeIds) {
        return restaurantRepository.findAllById(placeIds);
    }

    public List<Restaurant> findAll() {
        return restaurantRepository.findAll();
    }
    @Transactional
    public void updateRating(Integer placeId, Double rating, Integer count) {
        Restaurant restaurant = restaurantRepository.findById(placeId)
                .orElseThrow(() -> new IllegalArgumentException("없음"));
        restaurant.setRating(rating);
        restaurant.setReviewCount(count);
        // save() 호출 필요 없음
    }


    public boolean isRestaurantExistsByPlaceId(Integer placeId) {
        return restaurantRepository.existsByPlaceId(placeId);
    }


    public List<Integer> findNearbyRestaurantByPlaceId(float lat, float lng, int radius) {

        List<Restaurant> restaurants = restaurantRepository.findNearbyRestaurants(lat, lng, radius);
        System.out.println("근처 식당 수: " + restaurants.size());

        List<Integer> result = new ArrayList<>();

        for (Restaurant r : restaurants) {
            Integer placeId = r.getPlaceId();
            result.add(placeId);
        }
        return result;
    }

    public List<Restaurant> getAllRestaurants() {
        return restaurantRepository.findAll();
    }

    public List<Integer> findByCategory(List<String> keywords) {
        List<Integer> result = new ArrayList<>();

        // 모든 식당을 가져오고 (또는 필요한 범위만 가져오도록 개선 가능)
        List<Restaurant> allRestaurants = restaurantRepository.findAll();

        for (Restaurant restaurant : allRestaurants) {
            String category = restaurant.getCategory();
            if (category == null) continue;

            for (String keyword : keywords) {
                if (category.contains(keyword)) {
                    result.add(restaurant.getPlaceId());
                    break; // 하나라도 매칭되면 추가 후 다음 식당으로
                }
            }
        }

        return result;
    }
    public List<Integer> findByContext(List<String> keywords) {
        if (keywords == null || keywords.isEmpty()) {
            return Collections.emptyList(); // 또는 예외를 던져도 됨
        }

        Set<Integer> matchedPlaceIds = new HashSet<>();

        for (String keyword : keywords) {
            // OR 조건이면 그냥 keyword, AND 조건이면 "+" 붙여서 전달
            String formatted = "+" + keyword;  // AND 조건 예시
            List<Integer> ids = reviewRepository.findPlaceIdsByReviewKeyword(formatted);
            matchedPlaceIds.addAll(ids);
        }

        return new ArrayList<>(matchedPlaceIds);
    }


}
