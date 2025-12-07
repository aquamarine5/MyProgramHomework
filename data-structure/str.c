#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
void count(char s[], int *pzm, int *psz)
{
    char *p = s;
    while (*p != '\0')
    {
        if (isdigit(*p))
            ++(*psz);
        else if (isalpha(*p))
            ++(*pzm);
        ++p;
    }
}
void insert(char *s, char *t, int pos)
{
    char c[100];
    strcpy(c, s + pos - 1);
    s[pos - 1] = '\0';
    strcat(s, t);
    strcat(s, c);
}
int main()
{
    char s[200], t[50];
    int pos;

    printf("请输入字符串s：");
    scanf("%s", s);
    printf("\n请输入字符串t：");
    scanf("%s", t);

    printf("\n输入插入的位置（位置从1开始）：");
    scanf("%d", &pos);
    printf("\n字符串插入后的新字符串为：");
    insert(s, t, pos);
    printf("%s", s);
    return 0;
}