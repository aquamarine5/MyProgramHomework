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

void sortRowsByEachRowAverage(int **value, int n)
{
    int *rowSum = (int *)calloc(n, sizeof(int)), temp;
    for (int i = 0; i < n; ++i)
        for (int j = 0; j < n; ++j)
            rowSum[i] += value[i][j];
    for (int i = 0; i < n; ++i)
    {
        int minIndex = i;
        for (int j = i + 1; j < n; j++)
            if (rowSum[j] < rowSum[minIndex])
                minIndex = j;
        if (minIndex != i)
        {
            // for (int k = 0; k < n; ++k)
            // {
            //     temp = value[minIndex][k];
            //     value[minIndex][k] = value[i][k];
            //     value[i][k] = temp;
            // }
            int *tempRow = value[i];
            value[i] = value[minIndex];
            value[minIndex] = tempRow;

            temp = rowSum[i];
            rowSum[i] = rowSum[minIndex];
            rowSum[minIndex] = temp;
        }
    }
    free(rowSum);
}
void printMatrix(int **matrix, int n)
{
    for (int i = 0; i < n; ++i)
    {
        for (int j = 0; j < n; ++j)
            printf("%4d ", matrix[i][j]);
        printf("\n");
    }
}
int main()
{
    int n = 4;

    int **matrix = (int **)malloc(n * sizeof(int *));
    for (int i = 0; i < n; i++)
        matrix[i] = (int *)malloc(n * sizeof(int));

    int testData[4][4] = {
        {10, 20, 5, 5}, // 和=40, 平均=10
        {1, 2, 3, 4},   // 和=10, 平均=2.5
        {9, 8, 90, 11}, // 和=40, 平均=10
        {5, 5, 5, 5}    // 和=20, 平均=5
    };

    for (int i = 0; i < n; i++)
        for (int j = 0; j < n; j++)
            matrix[i][j] = testData[i][j];

    printf("原始矩阵:\n");
    printMatrix(matrix, n);
    sortRowsByEachRowAverage(matrix, n);
    printf("\n按行平均值排序后的矩阵:\n");
    printMatrix(matrix, n);
    for (int i = 0; i < n; i++)
        free(matrix[i]);
    free(matrix);
    return 0;
}