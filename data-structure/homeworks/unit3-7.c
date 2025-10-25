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

typedef int *SPMatrixSingleVector;
SPMatrixSingleVector plus(SPMatrixSingleVector A, SPMatrixSingleVector B, int m, int n)
{
    SPMatrixSingleVector C = (SPMatrixSingleVector)calloc(MAXSIZE * 3 + 1, sizeof(int));
    int indexA = 0, indexB = 0, indexC = 0;
    while (A[indexA] != -1 && B[indexB] != -1)
    {
        int ax = A[indexA], ay = A[indexA + 1], av = A[indexA + 2], bx = B[indexB], by = B[indexB + 1], bv = B[indexB + 2];
        if (ax < bx || (ax == bx && ay < by))
        {
            C[indexC++] = ax;
            C[indexC++] = ay;
            C[indexC++] = av;
            indexA += 3;
        }
        else if (ax > bx || (ax == bx && ay > by))
        {
            C[indexC++] = bx;
            C[indexC++] = by;
            C[indexC++] = bv;
            indexB += 3;
        }
        else
        {
            C[indexC++] = ax;
            C[indexC++] = ay;
            C[indexC++] = av + bv;
            indexA += 3;
            indexB += 3;
        }
    }
    while (A[indexA] != -1)
    {
        for (int _ = 0; _ < 3; ++_)
            C[indexC++] = A[indexA++];
    }
    while (B[indexB] != -1)
    {
        for (int _ = 0; _ < 3; ++_)
            C[indexC++] = B[indexB++];
    }
    C[indexC] = -1;
    return C;
}