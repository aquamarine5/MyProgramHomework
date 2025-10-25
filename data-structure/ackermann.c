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

int ackByRecursion(int m, int n)
{
    if (m == 0)
        return n + 1;
    if (n == 0)
        return Ack(m - 1, 1);
    return Ack(m - 1, Ack(m, n - 1));
}

int buffer[100][100];

int Ack(int m, int n)
{
    int pm = m, pn = n;
    for (int j = 0; j < n; j++)
        buffer[0][j] = j + 1; // Ack(m,n)=n+1, m==0
    for (int i = 1; i < m; i++)
    {
        buffer[i][0] = buffer[i - 1][1]; // Ack(m,n)=Ack(m-1,1), n==0
        for (int j = 1; j < n; j++)
        {
            buffer[i][j] = buffer[i - 1][buffer[i][j - 1]];
        }
    }
    return buffer[m][n];
}