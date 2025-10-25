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

void strDelete(char *source, int index, int count)
{
    if (index >= strlen(source))
        return;
    // abcdefghij
    // 0123456789
    //    ^---^
    //    i=3,c=5
    //    length=4
    if (index + count >= strlen(source))
        source[index] = '\0';
    strcpy(source + index, source + index + count);
}
int main()
{
    char str[] = "aqua-quokka-marine5";
    strDelete(str, 4, 8);
    printf("%s", str);
}