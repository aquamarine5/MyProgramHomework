package org.aquamarine5.brainspark.exp10;

import java.util.Scanner;

public class MainMyRectangle {
    public static void main(String[] args){
        var scanner=new Scanner(System.in);
        System.out.print("Enter width:");
        double width=scanner.nextDouble();
        System.out.print("Enter height:");
        double height=scanner.nextDouble();
        var myRectangle=new MyRectangle(height,width);
        System.out.printf("The area of a rectangle with width %.2f and height %.2f is %.2f",
                myRectangle.width, myRectangle.height, myRectangle.getArea());
        System.out.printf("\nThe perimeter of a rectangle is %.2f\n",myRectangle.getPerimeter());
        myRectangle.draw();
    }
}
