#include <stdio.h>
void swap(int *a, int *b)
{
    int t = *a;
    *a = *b;
    *b = t;
}
int main()
{
    int a, b, c;
    scanf("%d %d %d", &a, &b, &c);
    if (a > b)
        swap(&a, &b);
    if (a > c)
        swap(&a, &c);
    if (b > c)
        swap(&b, &c);
    if (a + b > c)
    {
        if (a == b && b == c && a == c)
        {
            printf("Equilateral triangle\n");
        }
        else if (a == b || b == c || a == c)
        {
            printf("Isosceles triangle\n");
        }
        else
        {
            printf("Other triangle\n");
        }
    }
    else
    {
        printf("Not a triangle\n");
    }
}