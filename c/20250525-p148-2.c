#include <stdio.h>
#include <string.h>
#include <stdbool.h>

const char num[][10] = {"zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
                        "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"};
const char num2[][10] = {"twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"};
const char num3[][10] = {"hundred", "thousand", "million", "billion"};

inline void ifS(int n, bool isSpace)
{
    if (n > 1)
        printf("s");
    if (isSpace)
        printf(" ");
}

void printSmallNumber(int n)
{
    if (n < 100)
        if (n < 20)
            printf("%s", num[n]);
        else
        {
            printf("%s", num2[n / 10 - 2]);
            if (n % 10 != 0)
                printf(" %s", num[n % 10]);
        }
    else
    {
        int tmp = n / 100;
        printSmallNumber(tmp);
        printf(" %s", num3[0]);
        ifS(tmp, false);
        if (n % 100 != 0)
        {
            printf(" and ");
            printSmallNumber(n % 100);
        }
    }
}

inline void printLargeNumber(int n)
{
    int i = 0, tmp;
    const int largeUnits[] = {1000000000, 1000000, 1000};
    while (n > 1000 && i < 3)
    {
        if (n > largeUnits[i])
        {
            tmp = n / largeUnits[i];
            printSmallNumber(tmp);
            printf(" %s", num3[3 - i]);
            ifS(tmp, true);
            n %= largeUnits[i];
        }
        ++i;
    }
    printSmallNumber(n);
}

main()
{
    float number;
    printf("Enter a number: ");
    scanf("%f", &number);
    int prime = (int)number;
    float decimal = number - prime;
    if (number < 1000)
        printSmallNumber(prime);
    else
        printLargeNumber(prime);
    printf(number == 1.0 ? " dollar" : " dollars");
    if (decimal != 0)
    {
        printf(" ");
        printSmallNumber(decimal * 100);
        printf(" cents.");
    }
    else
        printf(".");
}