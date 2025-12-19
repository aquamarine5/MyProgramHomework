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

int sametree(BiTree t1, BiTree t2)
{
    if ((t1 == NULL && t2 != NULL) || (t1 != NULL && t2 == NULL))
        return 0;
    if (t1 == NULL && t2 == NULL)
        return 1;
    if (t1->data != t2->data)
        return 0;
    if (sametree(t1->lchild, t2->lchild) == 0)
    {
        return 0;
    }
    else
    {
        return sametree(t1->rchild, t2->rchild);
    }
}

BiTree CreateBitree(TElemType inorder[], TElemType postorder[], int lowin, int highin, int lowpost, int highpost)
{
    int i = lowin;
    BiTree bt = (BiTree)malloc(sizeof(BiTNode)); // 申请结点
    bt->data = postorder[highpost];              // 后序遍历的最后一个结点是根结点

    while (inorder[i] != postorder[highpost]) // 在中序序列中查找根结点
        i++;
    if (i == lowin)
        bt->lchild = NULL; // 处理左子树
    else
        bt->lchild = CreateBitree(inorder, postorder, lowin, i - 1, lowpost, lowpost + i - lowin - 1);
    if (i == highin)
        bt->rchild = NULL; // 处理右子树
    else
        bt->rchild = CreateBitree(inorder, postorder, i + 1, highin, lowpost + i - lowin, highpost - 1);
    return bt;
}

BiTree Reverse

int main()
{
    BiTree t1;
    BiTree t2;
    TElemType in[] = "DBEAFCG";                                              // 中序
    TElemType post[] = "DEBFGCA";                                            // 后序
    t1 = CreateBitree(in, post, 0, strlen(in) - 1, 0, strlen(post) - 1);     // 建立第一个二叉树
    TElemType in2[] = "DBEAFCG";                                             // 中序
    TElemType post2[] = "DEBFGCA";                                           // 后序
    t2 = CreateBitree(in2, post2, 0, strlen(in2) - 1, 0, strlen(post2) - 1); // 建立第二个二叉树
    printf("%d", sametree(t1, t2));
}