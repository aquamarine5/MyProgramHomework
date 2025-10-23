package org.aquamarine5.brainspark.exp4;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        var input = new Scanner(System.in);
        System.out.print("Enter a point with two coordinates: ");
        double x = input.nextDouble();
        double y = input.nextDouble();
        double hDistance = Math.abs(x);
        double vDistance = Math.abs(y);
        System.out.println("Point (%.2f, %.2f) is ".formatted(x, y) + ((hDistance <= 5 && vDistance <= 2.5) ? "in" : "not in" + " the rectangle."));
    }
}
