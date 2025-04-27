#include <stdio.h>
inline void reverse(int n)
{
    while (n > 0)
    {
        printf("%d", n % 10);
        n /= 10;
    }
}
int main()
{
    int n;
    printf("Please input a number:\n");
    scanf("%d", &n);
    reverse(n);
}