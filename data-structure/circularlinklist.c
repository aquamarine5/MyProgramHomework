/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdlib.h>

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

// create a circular linklist with the value of interval [start,end] by i++.
// CAUTION: head node without data is included the linklist, checking the node and head node are unequal is necessary.
// seealso: https://hbu.alphacoding.cn/courses/13174/learn/5e736f6c7d87e00fb3165792 (alphacoding-2.7::main())
LinkList createIncreasedRange(int start, int end)
{
    LinkList list = (LinkList)malloc(sizeof(LNode));
    list->next = list; // circular
    LNode *curr = list, *temp;
    for (int i = start; i <= end; i++)
    {
        // insert at tail
        temp = (LNode *)malloc(sizeof(LNode));
        temp->data = i;
        // [L] -> [1] -> [2] -> [3]    [4]
        //  ^                    |      ^temp
        //  \--------------------/
        //                       ^curr

        temp->next = curr->next;
        // [L] -> [1] -> [2] -> [3]    [4]
        //  ^                    |      |
        //  \--------------------/------/
        //                       ^curr

        curr->next = temp;
        // [L] -> [1] -> [2] -> [3] -> [4]
        //  ^                    x      |
        //  \---------------------------/
        //                       ^curr

        curr = curr->next;
        // [L] -> [1] -> [2] -> [3] -> [4]
        //  ^                           |
        //  \---------------------------/
        //                              ^curr
    }
    return list;
}

// traverse the circular linklist forever, remove the element if the index%3==0,
// when the linklist only have one element, traversing stopped and return the only element.
// https://hbu.alphacoding.cn/courses/13174/learn/5e736f6c7d87e00fb3165792
// alphacoding-2.7
int game(LinkList L)
{
    LNode *curr = L->next, *prev = L;
    int index = 1;
    //  [L] -> [1] ----\
    //   ^             |
    //   \-------------/
    while (L->next->next != L)
    {
        if (curr == L)
        {
            prev = curr;
            curr = curr->next;
            continue;
        }
        if (index % 3 == 0)
        {
            // i: ...  2      3      4      5
            // [L] -> [1] -> [2] -> [1] -> [4]
            //  ^                           |
            //  \---------------------------/
            //         ^prev  ^curr

            // if index+%3==0

            // i: ...  2      3      4      5
            //         /-------------\
            //         |             ↓
            // [L] -> [1]    [2]-x->[1] -> [4]
            //  ^                           |
            //  \---------------------------/
            //         ^prev  ^curr
            prev->next = curr->next;
            free(curr);

            // i: ...  2      3      4      5
            //         /-------------\
            //         |             ↓
            // [L] -> [1]    [2]-x->[1] -> [4]
            //  ^                           |
            //  \---------------------------/
            //         ^prev         ^curr
            curr = prev->next;
        }
        else
        {
            prev = curr;
            curr = curr->next;
        }
        index++;
    }
    return curr->data;
}

int main()
{
    LinkList L = createIncreasedRange(1, 100);
    printf("%d", game(L));
    return 0;
}