package org.aquamarine5.brainspark.exp10;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
public class MyRectangle {
    @Getter
    double height=1;
    double width=1;

    public MyRectangle(double w){
        this.width=w;
        this.height=w;
    }

    public double getPerimeter(){
        return 2*(height+width);
    }
    public double getArea(){
        return height*width;
    }

    public void draw(){
        for (int i = 0; i < this.width; i++)
            System.out.print("*");
        System.out.println();
        for (int i = 0; i < this.height - 2; i++) {
            System.out.print("*");
            for (int j = 0; j < this.width-2; j++)
                System.out.print(" ");
            System.out.print("*");
            System.out.println();
        }
        for (int i = 0; i < this.width; i++)
            System.out.print("*");
    }
}
