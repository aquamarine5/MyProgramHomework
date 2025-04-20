#include <stdio.h>
inline float calculate(int n)
{
    return (float)n / (n + 2);
}
main()
{
    float r = 0.0;
    for (int i = 1; i <= 10 * 2; i += 2)
    {
        r += calculate(i);
    }
    printf("%f", r);
}