package com.feelrate.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;



@Getter @Setter
public class RestaurantRequestDto {
    @JsonProperty("place_id")
    private Integer placeId;
    private String name;
    private String address;
    private Double rating;
    private String url;
    private String category;
    private double latitude;
    private double longitude;


}
