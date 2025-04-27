#include <stdio.h>
int fun(int i)
{
    int result = 0, f = 1, digit;
    while (i > 0)
    {
        digit = i % 10;
        if (digit % 2 == 0)
        {
            result += digit * f;
            f *= 10;
        }
        i /= 10;
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