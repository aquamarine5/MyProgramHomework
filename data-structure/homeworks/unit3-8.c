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

typedef int *SymmetricMatrix;

inline int getValue(SymmetricMatrix A, int x, int y)
{
    return A[x < y ? (y * (y - 1) / 2 + x - 1) : (x * (x - 1) / 2 + y - 1)];
}

int *times(SymmetricMatrix A, SymmetricMatrix B, int n)
{
    // 0 . . .
    // 1 2 . .
    // 3 4 5 .
    // 6 7 8 9
    // --->
    int index = 0, zippedSize = (n + 1) * n / 2, sum = 0;
    int *C = (int *)calloc(zippedSize, sizeof(int));
    for (int x = 0; x < n; x++)
        for (int y = 0; y < n; y++)
        {
            int sum = 0;
            for (int k = 0; k < n; k++)
                sum += getValue(A, x, k) * getValue(A, k, y);
            C[(x - 1) * n + y - 1] = sum;
        }
    return C;
}