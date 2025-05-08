#include <stdio.h>
main()
{
    int a = 0;
    int *p = &a;
    int *q = p;
    printf("%d\n", a);
    *p = 5;
    printf("%d\n", a);
    *q = *p + 5;
    printf("%d\n", a); // 0
}
