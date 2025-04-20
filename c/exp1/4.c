#include <stdio.h>
#include <stdbool.h>
inline bool check(int n)
{
    return n % 3 == 0 && n % 5 != 0;
}
main()
{
    for (int i = 100; i <= 200; ++i)
    {
        if (check(i))
            printf("%d ", i);
    }
}