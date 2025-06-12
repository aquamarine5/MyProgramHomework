#include <stdio.h>
#include <string.h>
void r(char *str, int len)
{
    if (len == 0)
        return;
    printf("%c", str[len - 1]);
    r(str, len - 1);
}
int main()
{
    char str[100];
    printf("请输入字符串: ");
    scanf_s("%s", str);
    int len = strlen(str);
    printf("反转后的字符串: ");
    r(str, len);
    printf("\n");
    return 0;
}