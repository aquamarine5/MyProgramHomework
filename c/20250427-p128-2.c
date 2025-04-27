#include <stdio.h>
inline int prime(int n)
{
    if (n < 2)
        return -1;
    for (int i = 2; i * i <= n; i++)
    {
        if (n % i == 0)
            return 0;
    }
    return 1;
}
main()
{
    int n;
    printf("Please input a number:\n");
    scanf("%d", &n);
    if (prime(n) == 1)
        printf("%d is a prime number.\n", n);
    else if (prime(n) == 0)
        printf("%d is not a prime number.\n", n);
    else
        printf("Invalid input.\n");
}