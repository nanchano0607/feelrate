package com.feelrate.service;

import com.feelrate.domain.Menu;
import com.feelrate.domain.Restaurant;
import com.feelrate.domain.Review;
import com.feelrate.dto.ReviewRequestDto;
import com.feelrate.repository.RestaurantRepository;
import com.feelrate.repository.ReviewRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class ReviewService {

    private final RestaurantRepository restaurantRepository;
    private final ReviewRepository reviewRepository;

    public void saveReviews(Integer placeId, List<ReviewRequestDto> reviewsDto) {
        Restaurant restaurant = restaurantRepository.findById(placeId)
                .orElseThrow(() -> new IllegalArgumentException("식당이 존재하지 않습니다: " + placeId));

        for (ReviewRequestDto dto : reviewsDto) {
            Review review = new Review();
            review.setText(dto.getText());
            review.setRestaurant(restaurant);
            reviewRepository.save(review);
        }
    }

    public List<String> getReviewTexts(Integer placeId) {
        Restaurant restaurant = restaurantRepository.findById(placeId)
                .orElseThrow(() -> new IllegalArgumentException("식당이 존재하지 않습니다: " + placeId));

        List<Review> reviews = reviewRepository.findByRestaurant(restaurant);

        return reviews.stream()
                .map(Review::getText)
                .collect(Collectors.toList());
    }

}
