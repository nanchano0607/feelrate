package com.feelrate.repository;

import com.feelrate.domain.Menu;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.stream.Collectors;

public interface MenuRepository extends JpaRepository<Menu, Long> {
    List<Menu> findByRestaurant_PlaceId(Integer placeId);

    @Query("SELECT DISTINCT m.restaurant.placeId FROM Menu m WHERE m.name LIKE %:keyword%")
    List<Integer> findRestaurantIdsByMenuKeyword(@Param("keyword") String keyword);
}

