#include <stdio.h>
main()
{
    int n, d = 0;
    scanf("%d", &n);
    if (n == 0)
    {
        printf("1");
        return 0;
    }
    while (n > 0)
    {
        n /= 10;
        d++;
    }
    printf("%d", d);
}