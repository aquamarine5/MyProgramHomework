package org.aquamarine5.brainspark.exp9;


public class Main {
    public static void main(String[] args) {
        var myRectangle = new MyRectangle(4d, 40d);
        System.out.printf("The area of a rectangle with width %.2f and height %.2f is %.2f",
                myRectangle.width, myRectangle.height, myRectangle.getArea());
        System.out.printf("\nThe perimeter of a rectangle is %.2f",myRectangle.getPerimeter());
        var yourRectangle = new MyRectangle(3.5d, 35.9d);
        System.out.printf("The area of a rectangle with width %.2f and height %.2f is %.2f",
                yourRectangle.width, yourRectangle.height, yourRectangle.getArea());
        System.out.printf("\nThe perimeter of a rectangle is %.2f", yourRectangle.getPerimeter());
    }
}
