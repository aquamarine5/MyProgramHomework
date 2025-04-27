#include <stdio.h>
#include <stdbool.h>
inline bool check(int x)
{
    return x % 3 == 0 && x % 5 != 0;
}
int fun(int x)
{
    int result = 0;
    for (int i = 100; i <= x; ++i)
    {
        if (check(i))
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