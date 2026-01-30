/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define datatype int
#define result int
#define MAXSIZE 1000

#define END_FLAG 1215

#define SUCCESS 1
#define WRONG_INDEX -100
#define LIST_NO_SIZE -101
#define NO_RESULT -1
typedef char TElemType;
typedef struct BiTNode
{
    TElemType data;
    struct BiTNode *lchild, *rchild;
} BiTNode, *BiTree;

typedef BiTree Bitree;

int judgeSameBiTree(BiTree t1, BiTree t2)
{
    if ((t1 == NULL && t2 != NULL) || (t1 != NULL && t2 == NULL))
        return 0;
    if (t1 == NULL && t2 == NULL)
        return 1;
    if (t1->data != t2->data)
        return 0;
    if (judgeSameBiTree(t1->lchild, t2->lchild) == 0)
    {
        return 0;
    }
    else
    {
        return judgeSameBiTree(t1->rchild, t2->rchild);
    }
}

BiTree CreateBitree(TElemType inorder[], TElemType postorder[], int lowin, int highin, int lowpost, int highpost)
{
    int i = lowin;
    BiTree bt = (BiTree)malloc(sizeof(BiTNode));
    bt->data = postorder[highpost];
    while (inorder[i] != postorder[highpost])
        i++;
    if (i == lowin)
        bt->lchild = NULL;
    else
        bt->lchild = CreateBitree(inorder, postorder, lowin, i - 1, lowpost, lowpost + i - lowin - 1);
    if (i == highin)
        bt->rchild = NULL;
    else
        bt->rchild = CreateBitree(inorder, postorder, i + 1, highin, lowpost + i - lowin, highpost - 1);
    return bt;
}

void createBiTree(Bitree *T)
{
    char ch = getchar();
    if (ch == '#')
    {
        *T = NULL;
    }
    else
    {
        *T = (Bitree)malloc(sizeof(BiTNode));
        (*T)->data = ch;
        createBiTree(&(*T)->lchild);
        createBiTree(&(*T)->rchild);
    }
}

int countAllNodes(Bitree T)
{
    if (T == NULL)
        return 0;
    return 1 + countAllNodes(T->lchild) + countAllNodes(T->rchild);
}

int countLeafNodes(Bitree T)
{
    if (T == NULL)
        return 0;
    if (T->lchild == NULL && T->rchild == NULL)
        return 1;
    return countLeafNodes(T->lchild) + countLeafNodes(T->rchild);
}

int judgeFullBiTree(Bitree T)
{
    return countAllNodes(T) == (countLeafNodes(T) * 2 - 1);
}

int main()
{
    Bitree T = NULL;
    printf("请以先序遍历的方式输入一棵树（#表示结点没有子树）：");
    createBiTree(&T);
    if (judgeFullBiTree(T))
        printf("YES");
    else
        printf("NO");
    return 0;
}