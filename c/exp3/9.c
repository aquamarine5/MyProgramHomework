#include <stdio.h>
#include <string.h>
inline int pow(int a, int b)
{
    int result = 1;
    for (int i = 0; i < b; i++)
    {
        result *= a;
    }
    return result;
}
int main()
{
    char str[100];
    scanf("%s", str);
    int len = strlen(str), result = 0;
    for (int i = len - 1; i >= 0; i--)
    {
        result += pow(10, (len - i - 1)) * (str[i] - '0');
    }
    printf("%d\n", result);
}