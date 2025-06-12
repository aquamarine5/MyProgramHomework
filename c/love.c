#include "stdio.h"
#include "stdlib.h"
int strcon(char *s, char t)
{
    int count = 0;
    // s是存储字符串类型变量的地址
    // t是用户输入的要查找的字符
    while (*s != '\0') // 类型一致可以比较
    {
        if (*s == t)
        {
            return count;
        }
        s++; // s别忘了也要++
        count++;
    }
    return -1; // 没找到用户要的那个字符
}
int main()
{
    int a[100] = 1;
}
int fib(int n)
{
    if (n == 1 || n == 2)
        return 1;
    return fib(n - 1) + fib(n - 2);
}
