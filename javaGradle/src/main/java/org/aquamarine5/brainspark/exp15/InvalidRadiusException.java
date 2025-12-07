package org.aquamarine5.brainspark.exp15;

import lombok.Getter;

public class InvalidRadiusException extends Exception {
    @Getter
    private double radius;

    public InvalidRadiusException(double radius) {
        super("Invalid radius: " + radius);
        this.radius = radius;
    }
}

