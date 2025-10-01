/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define datatype int
#define result int
#define MAXSIZE 1000

#define END_FLAG 1215

#define SUCCESS 1
#define WRONG_INDEX -100
#define LIST_NO_SIZE -101
#define NO_RESULT -1

typedef struct LinkNode
{
    datatype data;
    struct LinkNode *next;
} LinkNode;

typedef LinkNode *LinkList;

typedef LinkNode LNode;
typedef LinkList LinkListWithTail;

// head is blank data
// [_blank] -> NULL -or- [datatype] -> [datetype]
// by default, we use LinkListWithTail as LinkList to follow the standard of alphacoding.
LinkListWithTail init()
{
    LinkList L = (LinkList)malloc(sizeof(LinkNode));
    L->next = NULL;
    return L;
}

// create at tail
// head without data
LinkListWithTail createInOrder()
{
    datatype value;
    LinkListWithTail L = init();
    LinkNode *tail = L;
    scanf("%d", &value);
    while (value != END_FLAG)
    {
        insertAtTail(tail, value);
        tail = tail->next;
    }
    return L;
}

// create at head
// head with data
LinkList createInReverse()
{
    datatype value;
    LinkList L = NULL;
    scanf("%d", &value);
    while (value != END_FLAG)
    {
        LinkNode *node = (LinkNode *)malloc(sizeof(LinkNode));
        node->data = value;
        node->next = L;
        L = node;
        // NULL (as L)
        // [node] -> NULL
        // [L] -> NULL (L=node)
        // [node] -> [L] -> NULL
        // [newL] -> [L] -> NULL (L=node)
        // Reversed order
    }
    return L;
}

int length(LinkListWithTail L)
{
    int i = 0;
    LinkNode *node = L;
    while (node->next != NULL)
    {
        node = node->next;
        i++;
    }
    return i;
}

LinkNode *get(LinkListWithTail L, int index)
{
    LinkNode *node = L;
    for (int i = 0; i < index; i++)
    {
        if (node->next == NULL)
            return NULL;
        node = node->next;
    }
    return node->next;
}

LinkNode *locate(LinkListWithTail L, datatype data)
{
    LinkNode *node = L->next;
    while (node != NULL)
        if (node->data == data)
            return node;
        else
            node = node->next;
    return NULL;
}

// insert at start, caution possible descending.
void append(LinkListWithTail L, datatype data)
{
    LinkNode *node = (LinkNode *)malloc(sizeof(LinkNode));
    node->data = data;
    node->next = L->next;
    L->next = node;
}
void print(LinkListWithTail L)
{
    LinkNode *temp = L->next;
    while (temp != NULL)
    {
        printf("%d ", temp->data);
        temp = temp->next;
    }
    printf("\n");
}
// insert front at index (start with 1)
// seealso: book.
result insert(LinkListWithTail L, datatype data, int index)
{
    // 0 1 2 3 4 5 length:6
    // 1 2 3 4 5 6 [7]
    if (length(L) < index)
        return WRONG_INDEX;
    // before: [i-2] -> [i-1, prev] -> [i*]
    //                    ^ get(L,index-1)
    // after : [i-2] -> [i-1, prev] -> [i, node] -> [i*]
    LinkNode *prev = get(L, index - 1);
    if (prev == NULL)
        return WRONG_INDEX;
    LinkNode *node = (LinkNode *)malloc(sizeof(LinkNode));
    node->data = data;
    node->next = prev->next;
    prev->next = node;
    return SUCCESS;
}
// delete an element at index (start with 1).
result erase(LinkListWithTail L, int index)
{
    LinkNode *prev = get(L, index - 1), *temp;
    if (index < 1 || prev == NULL)
        return WRONG_INDEX;
    temp = prev->next;
    prev->next = temp->next;
    free(temp);
    return SUCCESS;
}
// reversed a LinkList.
// https://hbu.alphacoding.cn/courses/13174/learn/5e736f6b7d87e00fb316578d
// alphacoding-2.6
void reverse(LinkList L)
{
    LNode *node = L->next, *temp;
    L->next = NULL;
    while (node != NULL)
    {
        // [L]-->[1]-->[2]-->...
        //       ^node
        // [L]-->NUL  (L->next = NULL; executed before `while`)

        // [L]   [1]-->[2]-->...
        //        ^node ^temp
        temp = node->next;

        // [1]-->NUL   [2]-->...
        //  ^node       ^temp
        node->next = L->next;

        // [L]-->[1]-->NUL   [2]-->...
        //  ^L    ^node
        L->next = node;

        // [L]-->[1]-->NUL   [2]-->...
        //                    ^node
        node = temp;
    }
}

// remove the duplicated element.
void deduplication(LinkList L)
{
    LNode *node = L->next, *iter, *temp;
    while (node->next)
    {
        iter = node;
        while (iter->next)
        {
            // [1.] -> [2.] -> [1.] -> [4.]
            // node
            // iter    next
            //         iter    next        *current
            // [1.] -> [2.] -> [4.]
            if (node->data == iter->next->data)
            {
                temp = iter->next;
                iter->next = temp->next;
                free(temp);
            }
            iter = iter->next;
        }
        node = node->next;
    }
}

// merge ascending LinkList A and B into a descending LinkList C.
// https://hbu.alphacoding.cn/courses/13174/learn/5e736f6b7d87e00fb316578d
// alphacoding-2.5
int merge(LinkList A, LinkList B, LinkList C)
{
    LNode *ta = A->next, *tb = B->next, *temp = C;
    C->next = NULL;
    while (ta != NULL && tb != NULL)
    {
        if (ta->data > tb->data)
        {
            if (temp->data == tb->data)
            {
                tb = tb->next;
                continue;
            }
            // LListA: [1]  [2]  [5]
            //                    ^ta
            // LListB: [3]  [4]
            //          ^tb
            // ta>tb
            temp = tb;

            // LListB: [3]  [4]
            //          ^tp  ^tb
            tb = tb->next;

            // LListC: [_]  [2]  [1]
            //          ^C   ^Cnext
            // LListC: [_]  [3]->[2]  [1]
            //          ^C   ^tp  ^Cnext
            temp->next = C->next;

            // LListC: [_]x>[2]  [1]
            //          ^C   ^Cnext
            // LListC: [_]->[3]->[2]  [1]
            //          ^C   ^tp  ^Cnext
            C->next = temp;
        }
        else
        {
            if (temp->data == ta->data)
            {
                ta = ta->next;
                continue;
            }
            temp = ta;
            ta = ta->next;
            temp->next = C->next;
            C->next = temp;
        }
    }
    while (ta != NULL)
    {
        temp = ta;
        ta = ta->next;
        temp->next = C->next;
        C->next = temp;
    }
    if (tb != NULL)
    {
        temp = tb;
        tb = tb->next;
        temp->next = C->next;
        C->next = temp;
    }
    return 1;
}

int main()
{
    LinkList a = init(), b = init(), c = init();
    for (int i = 19; i >= 1; i -= 2)
        append(a, i);
    for (int i = 20; i >= 2; i -= 3)
        append(b, i);
    print(a);
    print(b);
    reverse(b);
    print(b);
    merge(a, b, c);
    print(c);
    return 0;
}