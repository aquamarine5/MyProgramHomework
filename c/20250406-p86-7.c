#include <stdio.h>
inline int isPerfect(int n)
{
    int sum = 0;
    for (int i = 1; i <= n / 2; ++i)
    {
        if (n % i == 0)
            sum += i;
    }
    return sum;
}

main()
{
    int n = 0;
    for (int i = 2; i <= 10000; i++)
    {
        if (isPerfect(i) == i)
        {
            printf("%d\n", i);
        }
    }
    return 0;
}