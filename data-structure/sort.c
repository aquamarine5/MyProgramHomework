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

typedef struct LNode
{
    int data;
    struct LNode *next;
} LNode, *LinkList;

void InsertSort(int *L, int length)
{
    int j;
    for (int i = 1; i < length; ++i)
    {
        if (L[i] < L[i - 1])
        {
            int temp = L[i];
            for (j = i - 1; j >= 0 && L[j] > temp; --j)
            {
                L[j + 1] = L[j];
            }
            L[j + 1] = temp;
        }
    }
}
void Create_LinkList(LinkList *L, int n)
{
    *L = (LinkList)malloc(sizeof(LNode));
    (*L)->next = NULL;
    LinkList rear;
    rear = *L;
    for (int i = 0; i < n; i++)
    {
        LinkList p = (LinkList)malloc(sizeof(LNode));
        p->next = NULL;
        printf("单链表中第%2d个元素是：", i + 1);
        scanf("%d", &p->data);
        rear->next = p;
        rear = p;
    }
}

void print_LinkList(LinkList L)
{
    LinkList p = L;
    while (p->next != NULL)
    {
        p = p->next;
        printf("%d ", p->data);
    }
}

void SelectSort(LinkList *L)
{
    LNode *p, *q, *min;
    int temp;

    if (L == NULL || *L == NULL)
        return;

    for (p = (*L)->next; p != NULL; p = p->next)
    {
        min = p;
        for (q = p->next; q != NULL; q = q->next)
        {
            if (q->data < min->data)
            {
                min = q;
            }
        }
        if (min != p)
        {
            temp = p->data;
            p->data = min->data;
            min->data = temp;
        }
    }
}

int main()
{
    int a[] = {49, 38, 65, 97, 76, 13, 27, 51};
    int n = sizeof(a) / sizeof(a[0]);
    InsertSort(a, n);
    int i;
    for (i = 0; i < n; i++)
        printf("%d ", a[i]);
    printf("\n");

    // Test SelectSort
    printf("Testing SelectSort on Linked List:\n");
    int b[] = {49, 38, 65, 97, 76, 13, 27, 51};
    int m = sizeof(b) / sizeof(b[0]);
    LinkList list = (LinkList)malloc(sizeof(LNode));
    list->next = NULL;
    LinkList tail = list;

    // Create list
    for (int k = 0; k < m; k++)
    {
        LNode *node = (LNode *)malloc(sizeof(LNode));
        node->data = b[k];
        node->next = NULL;
        tail->next = node;
        tail = node;
    }

    SelectSort(&list);

    // Print list
    print_LinkList(list);
    printf("\n");

    return 0;
}
