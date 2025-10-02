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

// remove the duplicated element.
// https://hbu.alphacoding.cn/courses/13174/learn/1selycxzae57xqkorfrz
// alphacoding-2.10
void deduplication(LinkList L)
{
    LNode *node = L->next, *iter, *temp;
    while (node->next)
    {
        iter = node;
        while (iter->next)
        {
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            // iter    i.nx
            // node.data != i.nx.data
            // (@tips: i.nx=iter.next)

            // $$ next $$
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            //         iter    i.nx                 (iter = iter->next;)
            // node.data == i.nx.data

            // $$ executed `if` $$                  (if(node->data == iter->next->data))
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            //         iter    i.nx
            //                 temp                 (temp = iter->next;)

            //          /---------------\
            //          |               ↓
            // [1.] -> [2.]    x__x -> [5.]         (iter->next = temp->next;)
            // node
            //         iter    i.nx
            //                 temp    t.nx         (free(temp);)
            if (node->data == iter->next->data)
            {
                temp = iter->next;
                iter->next = temp->next;
                free(temp);
            }
            else
            {
                iter = iter->next;
            }
        }
        if (node->next == NULL)
            break;
        node = node->next;
    }
}

// reversed a LinkList by inserting the element at head pointer. Time complexity is O(n).
// https://hbu.alphacoding.cn/courses/13174/learn/5e736f6b7d87e00fb316578d
// alphacoding-2.6
void reverse(LinkList L)
{
    LNode *node = L->next, *temp;
    L->next = NULL;
    while (node != NULL)
    {
        // insert next element to head pointer

        // [L]-->[1]-->[2]-->[3]-->...
        //       ^node

        // [L]-->NUL  (L->next = NULL; executed before `while`)

        // [L]   [1]-->[2]-->[3]-->...
        //        ^node ^temp
        temp = node->next;

        // [1]-->NUL   [2]-->[3]-->...
        //  ^node       ^temp
        node->next = L->next;

        // [L]-->[1]-->NUL   [2]-->[3]-->...
        //  ^L    ^node
        L->next = node;

        // [L]-->[1]-->NUL   [2]-->[3]-->...
        //                    ^node
        node = temp;

        // (later)
        // [L]-->[2]-->[1]-->NUL   [3]-->...
        //                          ^node
    }
}

// reversed a LinkList and the time complexity of algorithm is O(1),
// let all connections reversed, do not insert anything.
// before: [x] -> [y] ; after: [x] <- [y]
// https://hbu.alphacoding.cn/courses/13174/learn/azh019zdddmfmvpq2jke
// alphacoding-2.9
void reverseEnhanced(LinkList L)
{
    LNode *curr = L->next, *temp, *prev = L;
    // [L]  -> [1] -> [2] -> [1] -> [4] (before)
    //  ^prev   ^curr

    // [L] <=> [1] -> [2] -> [1] -> [4] (after, circular, L->next=1, 1->next=L)
    //  ^prev   ^curr

    while (curr->next != NULL)
    {
        // [1] -> [2] -> [1] -> [4]
        //  ^prev  ^curr  ^temp
        temp = curr->next;

        // [1] <= [2]    [1] -> [4]
        //  ^prev  ^curr  ^temp
        curr->next = prev;

        // [1] <= [2]    [1] -> [4]
        //  ^prev  ^curr  ^temp  (before)
        //         ^prev  ^curr  (after )
        prev = curr;
        curr = temp;
    }
    //  /-----------\
    //  |           ↓
    // [L] <------ [1] <= [2] <= [1]<-?-[4]    NULL
    //  ^L                        ^prev  ^curr
    // (the `while` ended but curr->next=prev haven't executed.)

    //  /-----------\
    //  |           ↓
    // [L] <------ [1] <= [2] <= [1] <= [4]    NULL
    //  ^L                        ^prev  ^curr
    curr->next = prev;

    //  /-----------\
    //  |           ↓
    // [L]  NULL<= [1] <= [2] <= [1] <= [4]    NULL
    //  ^L                        ^prev  ^curr
    L->next->next = NULL;

    //  /--------------------------------\
    //  |                                ↓
    // [L]  NULL<= [1] <= [2] <= [1] <= [4]    NULL
    //  ^L                        ^prev  ^curr
    L->next = curr;
}

// merge ascending LinkList A and B into a *uninitialized* *ascending* LinkList C.
// https://hbu.alphacoding.cn/courses/13174/learn/elssfox2bx43nnarqo6w
// seealso: mergeAscending()
// alphacoding-2.8
void mergeAscendingWithoutLinkListC(LinkList A, LinkList B, LinkList *C)
{
    LNode *ta = A->next, *tb = B->next, *tc;
    (*C) = (LinkList)malloc(sizeof(LNode));
    (*C)->next = NULL;
    tc = *C;
    while (ta != NULL && tb != NULL)
    {
        if (ta->data > tb->data)
        {
            tc->next = tb;
            tc = tb;
            tb = tb->next;
        }
        else if (ta->data < tb->data)
        {
            tc->next = ta;
            tc = ta;
            ta = ta->next;
        }
        else
        {
            tc->next = ta;
            tc = ta;
            ta = ta->next;
            LNode *temp = tb->next;
            free(tb);
            tb = temp;
        }
    }
    tc->next = (ta != NULL) ? ta : tb;
}

// merge ascending LinkList A and B into a *ascending* LinkList C.
void mergeAscending(LinkList A, LinkList B, LinkList C)
{
    LNode *ta = A->next, *tb = B->next, *tc = C;
    C->next = NULL;
    while (ta != NULL && tb != NULL)
    {
        if (ta->data > tb->data)
        {
            tc->next = tb;
            tc = tb;
            tb = tb->next;
        }
        else if (ta->data < tb->data)
        {
            tc->next = ta;
            tc = ta;
            ta = ta->next;
        }
        else
        {
            tc->next = ta;
            tc = ta;
            ta = ta->next;
            LNode *temp = tb->next;
            free(tb);
            tb = temp;
        }
    }
    tc->next = (ta != NULL) ? ta : tb;
}

// merge ascending LinkList A and B into a *descending* LinkList C.
// https://hbu.alphacoding.cn/courses/13174/learn/5e736f6b7d87e00fb316578d
// alphacoding-2.5
int mergeDescending(LinkList A, LinkList B, LinkList C)
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

// mix the same elements of LinkList A and LinkList B to LinkList C
// https://hbu.alphacoding.cn/courses/13174/learn/75xrzr5vihcdklopxveq
// alphacoding-2.9
void mix(LinkList *A, LinkList *B, LinkList *C)
{
    LNode *pa = (*A)->next, *pb = (*B)->next, *pc = *C = (LNode *)malloc(sizeof(LNode)), *temp;
    pc->next = NULL;
    // A: [1] [2] [4] [5]
    //     ^pa
    // B: [1] [3] [5]
    //     ^pb
    while (pa != NULL && pb != NULL)
    {
        if (pa->data == pb->data)
        {
            pc->next = pa;
            pc = pa;
            pa = pa->next;
            temp = pb->next;
            free(pb);
            pb = temp;
            // A: [1] [2] [4] [5]
            //         ^pa
            // B: [1] [3] [5]
            //         ^pb
        }
        else if (pa->data > pb->data)
        {
            pb = pb->next;
            // A: [1] [2] [4] [5]
            //             ^pa
            // B: [1] [3] [5]
            //         ^pb
        }
        else
        {
            pa = pa->next;
            // A: [1] [2] [4] [5]
            //             ^pa
            // B: [1] [3] [5]
            //             ^pb
        }
    }
}

// head is blank data
// [_blank] -> NULL -or- [datatype] -> [datetype]
// by default, we use LinkListWithTail as LinkList to follow the standard of alphacoding.
LinkListWithTail init()
{
    LinkList L = (LinkList)malloc(sizeof(LinkNode));
    L->next = NULL;
    return L;
}

// insert at start, caution possible descending.
void append(LinkListWithTail L, datatype data)
{
    LinkNode *node = (LinkNode *)malloc(sizeof(LinkNode));
    node->data = data;
    node->next = L->next;
    L->next = node;
}

// create at tail, head pointer *without* data
LinkListWithTail createInOrder()
{
    datatype value;
    LinkListWithTail L = init();
    LinkNode *tail = L;
    scanf("%d", &value);
    while (value != END_FLAG)
    {
        append(tail, value);
        tail = tail->next;
    }
    return L;
}

// create at head, head pointer *with* data
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

// locate the node of linklist by finding the data.
// https://hbu.alphacoding.cn/courses/13174/learn/51p1ko5x3taq75jprm9m
// alphacoding-2.4
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

// print the linklist.
// https://hbu.alphacoding.cn/courses/13174/learn/0rt7by1fnfoxsc43n650
// alphacoding-2.1
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

// insert front at index (start with 1).
// https://hbu.alphacoding.cn/courses/13174/learn/yfkd0eqtomaacrmirrz0
// seealso: book.
// alphacoding-2.2
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
// https://hbu.alphacoding.cn/courses/13174/learn/brp50uhvuc2mlpiitrff
// alphacoding-2.3
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

int main()
{
    LinkList a = init(), b = init(), c;
    for (int i = 19; i >= 1; i -= 2)
        append(a, i);
    for (int i = 20; i >= 2; i -= 3)
        append(b, i);
    print(a);
    reverseEnhanced(a);
    print(a);
    return 0;
}