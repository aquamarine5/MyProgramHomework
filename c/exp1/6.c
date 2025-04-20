#include <stdio.h>
inline void printBlank(int n)
{
    for (int i = 0; i < n; i++)
    {
        printf(" ");
    }
}
inline void printStar(int n)
{
    int s = (n * 2) - 1;
    for (int i = 1; i <= s; i++)
    {
        printf("* ");
    }
}
main()
{
    int v;
    scanf("%d", &v);
    int size = v * 2 + 1;
    for (int i = 1; i <= v; i++)
    {
        int diff = (v - i) * 2;
        printBlank(diff);
        printStar(i);
        printf("\n");
    }
}