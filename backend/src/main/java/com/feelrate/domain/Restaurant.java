package com.feelrate.domain;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

import java.util.ArrayList;
import java.util.List;

@Entity
@Getter
@Setter
@Table(name = "restaurant")
public class Restaurant {

    @Id
    private Integer placeId;  // ← 이걸 PK로 사용

    @Column(nullable = false)
    private String name;
    private String address;
    private Double rating;
    private Integer reviewCount;
    @Column(length = 1000)
    private String url;
    private double latitude;
    private double longitude;



    @OneToMany(mappedBy = "restaurant", cascade = CascadeType.ALL)
    @JsonIgnoreProperties("restaurant")
    private List<Menu> menus = new ArrayList<>();


    @OneToMany(mappedBy = "restaurant", cascade = CascadeType.ALL)
    @JsonManagedReference
    private List<Review> reviews = new ArrayList<>();
    private String category;

}