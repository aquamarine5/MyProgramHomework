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
    int *columnElementsSum = (int *)calloc(A->columnCount, sizeof(int));
    for (int j = 0; j < A->columnCount; j++)
        columnElementsSum[j] = 0;
    for (int indexA = 0; indexA < A->valueCount; indexA++)
    {
        columnElementsSum[A->data[indexA].x] += A->data[indexA].v;
    }
    for (int columnIndex = 0; columnIndex < A->columnCount; columnIndex++)
    {
        if (columnElementsSum[columnIndex] == 0)
            continue;
        for (int indexB = 0; indexB < B->valueCount; indexB++)
        {
            C->data[indexC].x = columnIndex;
            C->data[indexC].y = B->data[indexB].x;
            C->data[indexC++].v = columnElementsSum[columnIndex] * B->data[indexB].v;
        }
    }
    free(columnElementsSum);
    C->valueCount = indexC;
    return C;
}