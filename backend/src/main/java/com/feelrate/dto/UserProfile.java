package com.feelrate.dto;

import java.util.Map;

public class UserProfile {
    private final String email;
    private final String name;

    public UserProfile(Map<String, Object> attributes) {
        this.email = (String) attributes.get("email");
        this.name = (String) attributes.get("name");

    }

    public String getEmail() { return email; }
    public String getName() { return name; }


}
