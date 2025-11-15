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
void Getnext(int next[], char t[])
{
    int j = 1, k = 0;
    next[1] = 0;
    while (j < strlen(t)) // j<t[0]
    {
        if (k == 0 || t[j] == t[k])
        {
            j++;
            k++;
            next[j] = k;
        }
        else
            k = next[k];
    }
}
// reference: https://www.cnblogs.com/aninock/p/13796006.html
void calculateLongestPrefixList(char source[], int next[])
{
    int strPosition = 1, comparePosition = 0;
    next[1] = 0; // 1-based
    int length = strlen(source);
    while (strPosition < length)
    {
        printf("%d %d %c\n", strPosition, comparePosition, source[strPosition]);
        if (comparePosition == 0 || source[strPosition] == source[comparePosition])
            next[++strPosition] = ++comparePosition;
        // source for strPosition   (0-based)
        // next for comparePosition (1-based)
        //    A  B  A  B  D  A  B  A  B  A
        //    0  1  2  3  4  5  6  7  8  9  (index, 0-based)
        // 0  1  2  3  4  5  6  7  8  9  10 (index, 1-based)
        // ?  0  1  1  2  1  1  2  ?  ?  ?  (next, 1-based)
        //          ^c=2           ^s=7
        // ?  0  1  1  2  1  1  2  3  ?  ?  (next, 1-based)
        //             ^c=3           ^s=8
        // ?  0  1  1  2  1  1  2  3  4  ?
        //                ^c=4           ^s=9 (D!=A)
        //             ^c=next[4], 1-based, fetch the previous element
        //          ^c=2                 ^s=9 (A==A)

        // if(source[next[compartPosition]]==source[strPosition])
        //     next[strPosition+1]=comparePosition+1
        else
            comparePosition = next[comparePosition];
    }
}

void findLongestCommonSubstring(char a[], char b[])
{
    int *nextA = (int *)calloc(sizeof(int), strlen(a) + 1), *nextB = (int *)calloc(sizeof(int), strlen(b) + 1);
    calculateLongestPrefixList(a, nextA);
    calculateLongestPrefixList(b, nextB);
}
int main()
{
    char a[] = "abaaacba";
    int v[11];
    calculateLongestPrefixList(a, v);
    for (int i = 0; i < 10; i++)
    {
        printf("%d ", v[i]);
    }
}