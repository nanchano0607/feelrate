package com.feelrate.dto;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class RatingRequestDto {
    private Double rating;
    private Integer reviewCount;
}
