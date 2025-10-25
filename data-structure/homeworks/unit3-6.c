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

typedef struct
{
    int x, y;
    datatype v;
} SPNode;
typedef struct
{
    int columnCount, rowCount, valueCount;
    SPNode data[MAXSIZE];
} SPMatrix;

SPMatrix *times(SPMatrix *A, SPMatrix *B)
{
    // -->row   ↑
    //          | column
    // [a b c d e f]                 [v . . . .]
    // [. . . . . .]                 [. . . . .]
    // [. . . . . .] x [z . . . .] = [. . . . .]
    // [. . . . . .]                 [. . . . .]
    // [. . . . . .]                 [. . . . .]
    // v=(a+b+c+d+e+f)*z
    SPMatrix *C = (SPMatrix *)malloc(sizeof(SPMatrix));
    C->rowCount = A->rowCount;
    C->columnCount = B->columnCount;
    int indexC = 0, previousColumnIndex = -1;
    int *rowElementsSum = (int *)calloc(A->rowCount, sizeof(int));
    for (int indexA = 0; indexA < A->valueCount; indexA++)
        rowElementsSum[A->data[indexA].x] += A->data[indexA].v;
    for (int rowIndex = 0; rowIndex < A->rowCount; rowIndex++)
    {
        if (rowElementsSum[rowIndex] == 0)
            continue;
        for (int indexB = 0; indexB < B->valueCount; indexB++)
        {
            C->data[indexC].x = rowIndex;
            C->data[indexC].y = B->data[indexB].x;
            C->data[indexC++].v = rowElementsSum[rowIndex] * B->data[indexB].v;
        }
    }
    free(rowElementsSum);
    C->valueCount = indexC;
    return C;
}