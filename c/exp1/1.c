#include <stdio.h>
inline int calculate(int n)
{
    int r = 0;
    for (int i = 1; i <= n; ++i)
    {
        r += i * i;
    }
    return r;
}
main()
{
    int a, r = 0;
    scanf("%d", &a);
    for (int i = 1; i <= a; ++i)
    {
        r += calculate(i);
    }
    printf("%d", r);
}