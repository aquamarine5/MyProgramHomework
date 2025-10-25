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

void strInsert(char *str, char *target, int index)
{
    if (index > strlen(str))
        return;

    char tail[100];
    strcpy(tail, str + index);
    str[index] = '\0';
    strcat(str, target);
    strcat(str, tail);
}

int main()
{
    char str[] = "aquamarine5";
    char target[] = "-quokka-";
    strInsert(str, target, 4);
    printf("%s", str);
}