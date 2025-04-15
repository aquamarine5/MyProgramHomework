#include <stdio.h>
main()
{
    printf("Please input 12 integers:\n");
    int a[3][4];
    int maxv = -1e9;
    int minv = 1e9;
    for (int i = 0; i < 3; ++i)
    {
        for (int j = 0; j < 4; ++j)
        {
            scanf("%d", &a[i][j]);
            if (a[i][j] > maxv)
            {
                maxv = a[i][j];
            }
            if (a[i][j] < minv)
            {
                minv = a[i][j];
            }
        }
    }
    printf("max=%d\n", maxv);
    printf("min=%d\n", minv);
}