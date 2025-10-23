package org.aquamarine5.brainspark.exp9;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@AllArgsConstructor
@NoArgsConstructor
public class MyRectangle {
    @Getter
    double height=1;
    double width=1;

    public double getPerimeter(){
        return 2*(height+width);
    }
    public double getArea(){
        return height*width;
    }
}
