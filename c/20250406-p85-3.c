#include <stdio.h>
main()
{
    int num = 0, result = 0;
    for (int i = 1; i <= 9; ++i)
    {
        num = num * 10 + i;
        result += num;
    }
    printf("%d\n", result);
}