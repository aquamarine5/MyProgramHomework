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

typedef struct BiNode
{
    datatype data;
    struct BiNode *left, *right;
} BiNode, *BiTree;

int findMaxValueByRecursion(BiTree root)
{
    if (root == NULL)
        return -0x3f3f3f3f;
    return max(findMaxValueByRecursion(root->left), max(findMaxValueByRecursion(root->right), root->data));
}

int findMaxValueWithoutRecursion(BiTree root)
{
    BiNode *stack[MAXSIZE], *p = root;
    int top = -1, maxValue = -0x3f3f3f3f;
    while (p != NULL || top != -1)
    {
        while (p != NULL)
        {
            maxValue = max(maxValue, p->data);
            stack[++top] = p;
            p = p->left;
        }
        if (top < 0)
            return maxValue;
        else
            p = stack[top--]->right;
    }
    return maxValue;
}