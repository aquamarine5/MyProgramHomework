#include <stdio.h>
#include <math.h>
typedef struct
{
    int x;
    int y;
    int z;
} Triangle;
Triangle inputTriangle()
{
    Triangle t;
    printf("Enter the lengths of the sides of the triangle (x y z): ");
    scanf("%d %d %d", &t.x, &t.y, &t.z);
    return t;
}
int isValidTriangle(Triangle t)
{
    return (t.x + t.y > t.z) && (t.x + t.z > t.y) && (t.y + t.z > t.x);
}
float calculateArea(Triangle t)
{
    float s = (t.x + t.y + t.z) / 2.0;
    return sqrt(s * (s - t.x) * (s - t.y) * (s - t.z));
}
int main()
{
    Triangle t = inputTriangle();
    if (isValidTriangle(t))
    {
        float area = calculateArea(t);
        printf("The area of the triangle is: %.2f\n", area);
    }
    else
    {
        printf("The lengths do not form a valid triangle.\n");
    }
    return 0;
}