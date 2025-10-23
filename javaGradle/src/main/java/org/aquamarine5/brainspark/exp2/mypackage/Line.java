package org.aquamarine5.brainspark.exp2.mypackage;

public class Line {
    public Point point1, point2;//直线的两点

    public Line(Point point1, Point point2)//构造方法，两点确定一条直线
    {
        this.point1 = point1;
        this.point2 = point2;
    }

    public double length()//返回直线长度
    {
        int a = point1.x - point2.x, b = point1.y - point2.y;
        return Math.sqrt(a * a + b * b);//数学类Math.sqrt（x）返回x的平方根
    }

    public String toString()//直线的描述字符串
    {
        return "一条直线，起点" + point1.toString() + "，终点" + point2.toString() + "，长度" + String.format("%1.2f", length());
    }
}
