package org.aquamarine5.brainspark.exp14;

import java.util.Scanner;

public class Quotient {
    public static void quotient(double a, double b) {
        System.out.println("The quotient is " + (a / b));
    }

    public static void quotientIf(double a, double b) {
        if (b == 0)
            System.out.println("Division by zero is not allowed.");
        else System.out.println("The quotient is " + (a / b));
    }

    public static void quotientWithException(double a, double b)
            throws ArithmeticException {
        if (b == 0)
            throw new ArithmeticException("Division by zero is not allowed.");
        else System.out.println("The quotient is " + (a / b));
    }

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        System.out.print("Enter two numbers: ");
        int a = scan.nextInt();
        int b = scan.nextInt();
        quotient(a, b);
        quotientIf(a, b);
        try {
            quotientWithException(a, b);
        } catch (ArithmeticException e) {
            System.out.println(e.getMessage());
        }
    }
}
