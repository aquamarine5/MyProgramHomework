#include <stdio.h>
main()
{
    int i = 1, maxv = 0, minv = 0;
    while (i != 0)
    {
        scanf("%d", &i);
        if (i > 0)
            maxv++;
        else if (i < 0)
        {
            minv++;
        }
    }
    printf("Number greater than 0: %d\nNumber of less than 0: %d\n", maxv, minv);
}