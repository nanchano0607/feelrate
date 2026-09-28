package com.feelrate.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@AllArgsConstructor
public class RatingAndCount {
    private Integer placeId;
    private Double rating;
    private Integer reviewCount;
}
