#include <stdio.h>
#include <string.h>
void swap(char *a, char *b)
{
    char temp;
    temp = *a;
    *a = *b;
    *b = temp;
}
main()
{
    char a[100];
    int i, j;
    scanf("%s", a);
    scanf("%d", &i);
    scanf("%d", &j);
    for (int k = i - 1; k < (i - 1 + (j - i + 1) / 2); k++)
    {
        swap(&a[k], &a[(j - 1) - (k - i + 1)]);
    }
    printf("%s", a);
}