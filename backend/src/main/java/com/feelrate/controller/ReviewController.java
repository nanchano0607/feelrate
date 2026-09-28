package com.feelrate.controller;

import com.feelrate.domain.Review;
import com.feelrate.dto.ReviewRequestDto;
import com.feelrate.service.ReviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequiredArgsConstructor
@RequestMapping("/api/restaurants")
public class ReviewController {

    private final ReviewService reviewService;

    @PostMapping("/{placeId}/reviews")
    public ResponseEntity<Void> saveReviews(@PathVariable("placeId") Integer placeId, @RequestBody List<ReviewRequestDto> reviewsDto)
    {
        reviewService.saveReviews(placeId, reviewsDto);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/{placeId}/reviews")
    public List<String> getReviewTexts(@PathVariable("placeId") Integer placeId) {
        return reviewService.getReviewTexts(placeId);
    }
}
