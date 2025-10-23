package org.aquamarine5.brainspark.exp3;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        var input = new Scanner(System.in);
        System.out.print(
                "Enter the investment amount, for example 120000.95: ");
        double investmentAmount = input.nextDouble();
        System.out.print("Enter annual interest rate, for example 8.25: ");
        double annualInterestRate = input.nextDouble();
        double monthlyInterestRate = annualInterestRate / 1200;
        System.out.print(
                "Enter number of years as an integer, \nfor example 5: ");
        int numOfYears = input.nextInt();
        double futureValue =
                investmentAmount * Math.pow(1 + monthlyInterestRate,
                        numOfYears * 12);
        System.out.print("Future value is " +
                (int) (futureValue * 100) / 100.0);
    }
}
