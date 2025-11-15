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

int getNodes(BiTree root)
{
    if (root == NULL)
        return 0;
    return getNodes(root->left) + getNodes(root->right) + 1;
}
