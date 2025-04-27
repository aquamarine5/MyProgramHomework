#include <stdio.h>
#include <stdbool.h>
inline bool prime(int x)
{
    if (x < 2)
        return false;
    for (int i = 2; i * i <= x; ++i)
    {
        if (x % i == 0)
            return false;
    }
    return true;
}

int fun(int x)
{
    int result = 0;
    for (int i = 2; i <= x; ++i)
    {
        if (prime(i))
        {
            result += i;
        }
    }
    return result;
}

int main()
{
    int n;
    scanf("%d", &n);
    printf("%d", fun(n));
    return 0;
}