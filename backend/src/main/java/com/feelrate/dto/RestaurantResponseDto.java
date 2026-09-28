package com.feelrate.dto;

import com.feelrate.domain.Review;
import lombok.Getter;
import lombok.Setter;
import java.util.List;


@Getter
@Setter
public class RestaurantResponseDto {
    private Integer placeId;
    private String name;
    private String address;
    private double rating;
    private Integer reviewCount;
    private String category;
    private List<Review> reviews;
    private String url;
}
