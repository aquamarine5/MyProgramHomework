#include <stdio.h>
#include <string.h>
char str[1000];
void fun(int index)
{
    putchar(str[strlen(str) - index]);
    if (index < strlen(str))
        fun(++index);
}
int main()
{
    scanf("%s", &str);
    fun(0);
}