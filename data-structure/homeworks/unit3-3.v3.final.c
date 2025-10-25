/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define datatype int
#define result int
#define MAXSIZE 1000

#define END_FLAG 1215

#define SUCCESS 1
#define WRONG_INDEX -100
#define LIST_NO_SIZE -101
#define NO_RESULT -1

char *findLongestCommonSubstring(char a[], char b[])
{
    int aLength = strlen(a), bLength = strlen(b), resultStartIndex = 0;
    int maxLength = 0;
    for (int i = 0; i < aLength; i++)
    {
        for (int j = 0; j < bLength; j++)
        {
            int currentLength = 0;
            while ((i + currentLength < aLength) && (j + currentLength < bLength) &&
                   (a[i + currentLength] == b[j + currentLength]))
            {
                currentLength++;
            }
            if (currentLength > maxLength)
            {
                maxLength = currentLength;
                resultStartIndex = i;
            }
        }
    }

    char *answer = (char *)malloc((maxLength + 1) * sizeof(char));
    strncpy(answer, a + resultStartIndex, maxLength);
    answer[maxLength] = '\0';
    return answer;
}