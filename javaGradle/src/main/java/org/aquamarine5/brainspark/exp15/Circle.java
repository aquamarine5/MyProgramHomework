package org.aquamarine5.brainspark.exp15;

import lombok.Getter;

public class Circle {
    @Getter
    private double radius;
    @Getter
    private static int numberOfObjects = 0;
    public Circle(){
        this(1.0);
    }
    public Circle(double radius){
        try{
            setRadius(radius);
            numberOfObjects++;
        } catch (InvalidRadiusException e){
            System.out.println(e.getMessage());
        }
    }
    public void setRadius(double radius)
            throws InvalidRadiusException{
        if(radius < 0)
            throw new InvalidRadiusException(radius);
        this.radius = radius;
    }
    public double findArea(){
        return radius * radius * Math.PI;
    }
}
