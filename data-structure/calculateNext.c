/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>

#define datatype int
#define result int
#define MAXSIZE 1215

void Get(char t[], int next[])
{
    int j = 1, k = 0;
    next[1] = 0;
    while (j < t[0])
    {
        if (k == 0 || t[j] == t[k])
        {
            printf("k=%d, j=%d, next[%d]=%d\n", k, j, j + 1, k + 1);
            next[++j] = ++k;
        }
        else
        {
            printf("k=%d, 回溯至=%d\n", k, next[k]);
            k = next[k];
        }
    }
}
int main()
{
    char t[] = " abaabcac";
    int next[9];
    Get(t, next);
    for (int i = 0; i < 9; i++)
    {
        printf("%d ", next[i]);
    }
}