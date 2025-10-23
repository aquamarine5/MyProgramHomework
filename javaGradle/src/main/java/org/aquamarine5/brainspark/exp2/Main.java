package org.aquamarine5.brainspark.exp2;

import org.aquamarine5.brainspark.exp2.mypackage.Point;

import org.aquamarine5.brainspark.exp2.mypackage.Line;

public class Main {
    public static void main(String[] args) {
        var point1 = new Point(0,0);
        var point2=new Point(40,30);
        System.out.println(new Line(point1,point2).toString());
    }
}