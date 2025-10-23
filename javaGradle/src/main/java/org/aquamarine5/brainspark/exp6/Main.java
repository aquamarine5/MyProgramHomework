package org.aquamarine5.brainspark.exp6;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        var input = new Scanner(System.in);
        System.out.print("Enter numbers: ");
        int number = input.nextInt();
        int max = number;
        int count = 1;
        while (number != 0) {
            number = input.nextInt();
            if (number > max) {
                max = number;
                count = 1;
            } else if (number == max)
                count++;
        }
        System.out.printf("The largest number is %d, The occurrence count of the largest number is %d%n", max, count);
    }
}
