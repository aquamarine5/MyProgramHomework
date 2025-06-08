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
    char t;
    char str[] = "HELLO,WORLD!";
    printf("请输入要查找的字符:");
    scanf_s("%c", &t);
    int length = strcon(str, t);
    if (length != -1)
    {
        printf("%c第一次出现在%d处\n", t, length);
    }
    else
    {
        printf("%c不存在于字符串中\n", t);
    }
    system("pause");
    return 0;
}
