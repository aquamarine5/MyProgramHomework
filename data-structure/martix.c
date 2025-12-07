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
#define MAXSIZE 1000

#define END_FLAG 1215

#define SUCCESS 1
#define WRONG_INDEX -100
#define LIST_NO_SIZE -101
#define NO_RESULT -1
#define max(a, b) (((a) > (b)) ? (a) : (b))
#define min(a, b) (((a) < (b)) ? (a) : (b))
#define ROW 3
#define COL 3

void Find(int arr[][COL], int row, int col)
{
    for (int i = 0; i < row; ++i)
    {
        for (int j = 0; j < col; ++j)
            scanf("%d", &arr[i][j]);
    }
    int rowMinValue[ROW], rowMaxValue[ROW], colMinValue[COL], colMaxValue[COL];
    int tempMin, tempMax;
    for (int i = 0; i < row; ++i)
    {
        tempMin = 0x3f3f3f3f;
        tempMax = -0x3f3f3f3f;
        for (int j = 0; j < col; ++j)
        {
            tempMin = min(tempMin, arr[i][j]);
            tempMax = max(tempMax, arr[i][j]);
        }
        rowMinValue[i] = tempMin;
        rowMaxValue[i] = tempMax;
    }
    for (int i = 0; i < col; ++i)
    {
        tempMin = 0x3f3f3f3f;
        tempMax = -0x3f3f3f3f;
        for (int j = 0; j < row; ++j)
        {
            tempMin = min(tempMin, arr[j][i]);
            tempMax = max(tempMax, arr[j][i]);
        }
        colMinValue[i] = tempMin;
        colMaxValue[i] = tempMax;
    }
    for (int i = 0; i < row; ++i)
    {
        for (int j = 0; j < col; ++j)
        {
            if (arr[i][j] == rowMaxValue[i] && arr[i][j] == colMinValue[j])
            {
                printf("该数组中存在鞍点arr[%d][%d] = %d", i, j, arr[i][j]);
                return;
            }
        }
    }
    printf("该数组中不存在鞍点！");
}

int main()
{
    int arr[ROW][COL] = {0};
    Find(arr, ROW, COL);
    return 0;
}