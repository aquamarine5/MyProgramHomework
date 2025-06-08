#include <stdio.h>
#include <stdbool.h>
inline bool check(int x)
{
    return x % 3 == 0 && x % 5 != 0;
}
void fun(int x)
{
    int result = 0;
    for (int i = 100; i <= x; ++i)
    {
        if (check(i))
        {
            printf("%d ", i);
        }
    }
}
int main()
{
    int n;
    scanf("%d", &n);
    fun(n);
    return 0;
}