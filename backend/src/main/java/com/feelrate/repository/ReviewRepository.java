package com.feelrate.repository;

import com.feelrate.domain.Restaurant;
import com.feelrate.domain.Review;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ReviewRepository extends JpaRepository<Review, Long> {

    // 특정 식당(placeId) 기준으로 리뷰 리스트 조회
    List<Review> findByRestaurant(Restaurant restaurant);

    @Query(value = """
            SELECT DISTINCT restaurant_id
            FROM review
            WHERE MATCH(text) AGAINST(:keyword IN BOOLEAN MODE)
            """, nativeQuery = true)
    List<Integer> findPlaceIdsByReviewKeyword(@Param("keyword") String keyword);
}
