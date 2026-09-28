package com.feelrate.repository;

import com.feelrate.domain.Restaurant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;


public interface RestaurantRepository extends JpaRepository<Restaurant, Integer> {
    boolean existsByPlaceId(Integer placeId);


    // 좌표 기반 반경 거리 내 음식점 검색
    @Query(value = """
        SELECT * FROM restaurant
        WHERE ST_Distance_Sphere(
            POINT(longitude, latitude), POINT(:lng, :lat)) < :radius
        """, nativeQuery = true)
    List<Restaurant> findNearbyRestaurants(
            @Param("lat") float lat,
            @Param("lng") float lng,
            @Param("radius") int radius
    );
}
