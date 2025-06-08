#include <stdio.h>
#include <string.h>
int main()
{
    char str[100], c, afterstr[100];
    printf("please input a string:");
    scanf("%s", str);
    printf("please input a character to delete:");
    scanf("\n%c", &c);
    int len = strlen(str), flag = 0, index = 0;
    for (int i = 0; i < len; i++)
    {
        if (str[i] != c)
        {
            afterstr[index++] = str[i];
            flag = 1;
        }
    }
    if (flag == 0)
    {
        printf("this character does not exist.\n");
    }
    else
    {
        afterstr[index] = '\0';
        printf("the string after deleting the character is:%s\n", afterstr);
    }
}