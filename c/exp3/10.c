#include <stdio.h>
#include <string.h>
main()
{
    char str[100], buffer[100], bufferi = 0;
    scanf("%s", str);
    for (int i = 0; i < strlen(str); i++)
    {
        if (str[i] >= '0' && str[i] <= '9')
        {
            buffer[bufferi++] = str[i];
        }
        else
        {
            if (bufferi == 0)
            {
                continue;
            }

            int num = 0;
            for (int j = 0; j < bufferi; j++)
            {
                num = num * 10 + (buffer[j] - '0');
            }
            printf("%d ", num);
            bufferi = 0;
        }
    }
}