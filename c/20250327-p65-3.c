#include <stdio.h>
int max(int a, int b)
{
    if (a > b)
    {
        return a;
    }
    else
    {
        return b;
    }
}
int min(int a, int b)
{
    if (a < b)
    {
        return a;
    }
    else
    {
        return b;
    }
}
int main()
{
    int a[4];
    for (int i = 0; i < 4; i++)
    {
        scanf("%d", &a[i]);
    }
    int minv = 999999;
    int maxv = -999999;
    for (int i = 0; i < 4; ++i)
    {
        minv = min(minv, a[i]);
        maxv = max(maxv, a[i]);
    }
    printf("max=%d\n", maxv);
    printf("min=%d\n", minv);
    return 0;
}