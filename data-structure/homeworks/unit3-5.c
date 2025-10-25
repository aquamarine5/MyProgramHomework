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
    int i, j;
    datatype v;
} SPNode;
typedef struct
{
    int columnCount, rowCount, valueCount;
    SPNode data[MAXSIZE];
} SPMatrix;

SPMatrix *add(SPMatrix *A, SPMatrix *B)
{
    SPMatrix *C = (SPMatrix *)malloc(sizeof(SPMatrix));
    C->rowCount = A->rowCount;
    C->columnCount = A->columnCount;
    int indexA = 0, indexB = 0, indexC = 0;
    while (indexA < A->valueCount && indexB < B->valueCount)
    {
        SPNode *nodeA = &A->data[indexA];
        SPNode *nodeB = &B->data[indexB];
        if (nodeA->i < nodeB->i || (nodeA->i == nodeB->i && nodeA->j < nodeB->j))
        {
            C->data[indexC++] = *nodeA;
            indexA++;
        }
        else if (nodeA->i > nodeB->i || (nodeA->i == nodeB->i && nodeA->j > nodeB->j))
        {
            C->data[indexC++] = *nodeB;
            indexB++;
        }
        else
        {
            C->data[indexC].i = nodeA->i;
            C->data[indexC].j = nodeA->j;
            C->data[indexC++].v = nodeA->v + nodeB->v;
            indexA++;
            indexB++;
        }
    }
    while (indexA < A->valueCount)
        C->data[indexC++] = A->data[indexA++];

    while (indexB < B->valueCount)
        C->data[indexC++] = B->data[indexB++];
    C->valueCount = indexC;
    return C;
}
