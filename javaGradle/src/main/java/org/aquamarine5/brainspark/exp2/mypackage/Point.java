package org.aquamarine5.brainspark.exp2.mypackage;

public class Point
{
    public int x, y;

    public Point(int x,int y)
    {
        this.x=x;
        this.y=y;
    }

    public Point()
    {
        this(0,0);
    }

    public Point(Point p)
    {
        this(p.x,p.y);
    }

    public String toString()
    {
        return"("+this.x+","+this.y+")";
    }
}