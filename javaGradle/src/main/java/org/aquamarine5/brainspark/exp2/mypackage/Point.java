package org.aquamarine5.brainspark.exp2.mypackage;

public class Point
{
    public int x, y;//成员变量

    public Point(int x,int y)//构造方法，以(x,y)构造Point对象
    {
        this.x=x;
        this.y=y;
    }

    public Point()//构造方法，重载，默认值（0，0）
    {
        this(0,0);
    }

    public Point(Point p)//拷贝构造方法
    {
        this(p.x,p.y);
    }

    public String toString()//成员方法，坐标点字符串描述，形式为（x,y）
    {
        return"("+this.x+","+this.y+")";
    }
}