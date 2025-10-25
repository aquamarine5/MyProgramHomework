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

int countSubstring(char *source, char *substring)
{
    int count = 0;
    int sourceLength = strlen(source);
    int subLength = strlen(substring);
    // abcdefgh (length=8)
    // 01234567
    // abc      (length=3)
    // 0<=i<=5
    for (int i = 0; i <= sourceLength - subLength; i++)
    {
        int j;
        for (j = 0; j < subLength; j++)
        {
            if (source[i + j] != substring[j])
                break;
        }
        if (j == subLength)
            count++;
    }
    return count;
}