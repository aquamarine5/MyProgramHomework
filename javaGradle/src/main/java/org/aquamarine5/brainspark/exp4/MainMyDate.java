package org.aquamarine5.brainspark.exp4;

import java.util.Scanner;

public class MainMyDate {
    public static void main(String[] args) {
        MyDate date=new MyDate(2024,10,15);
        System.out.println(date);
        System.out.println(MyDate.getThisYear());
        System.out.println(date.getThisYear());
    }
}
