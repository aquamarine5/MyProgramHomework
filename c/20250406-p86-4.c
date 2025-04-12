#include <stdio.h>
main()
{
    float result = 0.0;
    for (int i = 1; i <= 100; ++i)
    {
        result += (1.0 / i) * (i % 2 == 0 ? -1 : 1);
    }
    printf("%f\n", result);
}