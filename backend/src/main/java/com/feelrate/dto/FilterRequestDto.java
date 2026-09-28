package com.feelrate.dto;

import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter @Setter
public class FilterRequestDto {
    private List<String> keywords;

}
