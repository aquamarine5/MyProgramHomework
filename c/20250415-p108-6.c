#include <stdio.h>
main()
{
    int a[4] = {1, 3, 5, 7};
    int b[3] = {2, 4, 6};
    int c[7];
    for (int i = 0; i < 4; i++)
    {
        c[i] = a[i];
    }
    for (int i = 0; i < 3; i++)
    {
        c[i + 4] = b[i];
    }
    for (int i = 0; i < 7; ++i)
    {
        for (int j = i; j < 7; ++j)
        {
            if (c[i] > c[j])
            {
                int t = c[i];
                c[i] = c[j];
                c[j] = t;
            }
        }
    }
    for (int i = 0; i < 7; ++i)
    {
        printf("%d ", c[i]);
    }
}