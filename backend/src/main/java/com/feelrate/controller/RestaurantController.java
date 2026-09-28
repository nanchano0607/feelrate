package com.feelrate.controller;

import java.util.List;
import java.util.Optional;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.feelrate.domain.Restaurant;
import com.feelrate.dto.RatingAndCount;
import com.feelrate.dto.RatingRequestDto;
import com.feelrate.dto.RestaurantRequestDto;
import com.feelrate.service.RestaurantService;

import lombok.RequiredArgsConstructor;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/restaurants")
public class RestaurantController {

    private final RestaurantService restaurantService;


    @PostMapping
    public ResponseEntity<String> saveRestaurant(@RequestBody RestaurantRequestDto dto) {
        Restaurant restaurant = new Restaurant();
        restaurant.setPlaceId(dto.getPlaceId());
        restaurant.setName(dto.getName());
        restaurant.setAddress(dto.getAddress());
        restaurant.setRating(dto.getRating());
        restaurant.setUrl(dto.getUrl());
        restaurant.setCategory(dto.getCategory());
        restaurant.setLatitude(dto.getLatitude());
        restaurant.setLongitude(dto.getLongitude());


        restaurantService.save(restaurant);
        return ResponseEntity.ok("식당 저장 완료");
    }

    @GetMapping
    public ResponseEntity<List<Integer>> getNearByRestaurants(@RequestParam("lat") float lat, @RequestParam("lng") float lng, @RequestParam("radius") int radius) {
        List<Integer> restaurants = restaurantService.findNearbyRestaurantByPlaceId(lat, lng, radius);
        return ResponseEntity.ok(restaurants);
    }

    @PostMapping("/{placeId}/rating")
    public ResponseEntity<String> saveRestaurantRating(@PathVariable("placeId") Integer placeId, @RequestBody RatingRequestDto dto){
        Optional<Restaurant> restaurant = restaurantService.findByPlaceId(placeId);
        if(restaurant.isPresent()){
            restaurant.get().setRating(dto.getRating());
            restaurant.get().setReviewCount(dto.getReviewCount());
            restaurantService.updateRating(placeId, dto.getRating(), dto.getReviewCount());
            System.out.println("✅ 저장 전 확인: rating=" + restaurant.get().getRating() + ", reviewCount=" + restaurant.get().getReviewCount());
            return ResponseEntity.ok("평점과 리뷰 수가 저장되었습니다.");
        }
        else{
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("해당 placeId의 식당이 없습니다.");
        }
    }
    @GetMapping("/{placeId}")
    public boolean isRestaurantExists(@PathVariable("placeId") Integer placeId) {
        return restaurantService.isRestaurantExistsByPlaceId(placeId);
    }

    @GetMapping("/all")
    public ResponseEntity<List<Restaurant>> findAllRestaurants() {
        List<Restaurant> restaurants = restaurantService.findAll();
        return ResponseEntity.ok(restaurants);
    }

    @PostMapping("/ratingAndCount")
    public ResponseEntity<List<RatingAndCount>> findRestaurantsRatingAndCount(@RequestBody List<Integer> placeIds){
        List<RatingAndCount> restaurantsRatingAndCount = restaurantService.findByPlaceIdsRatingAndCount(placeIds);
        return ResponseEntity.ok(restaurantsRatingAndCount);
    }
    @PostMapping("/restaurants")
    public ResponseEntity<List<Restaurant>> findRestaurants(@RequestBody List<Integer> placeIds){
        List<Restaurant> restaurants = restaurantService.findByPlaceIds(placeIds);
        return ResponseEntity.ok(restaurants);
    }

}
