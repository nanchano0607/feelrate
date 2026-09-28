package com.feelrate.dto;

import com.feelrate.domain.Restaurant;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter @Setter
@AllArgsConstructor
public class RestaurantSimpleDto {
    private Integer placeId;
    private String name;
    private String address;
    private Double rating;

    public static RestaurantSimpleDto fromEntity(Restaurant restaurant) {
        return new RestaurantSimpleDto(
                restaurant.getPlaceId(),
                restaurant.getName(),
                restaurant.getAddress(),
                restaurant.getRating()
        );
    }
}

