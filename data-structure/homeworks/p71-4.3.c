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

#define SUCCESS 1
#define WRONG_INDEX -100
#define LIST_NO_SIZE -101
#define NO_RESULT -1

#pragma region SeqList
typedef struct
{
    datatype data[MAXSIZE];
    int last;
} SeqList;

SeqList *init()
{
    SeqList *L = (SeqList *)malloc(sizeof(SeqList));
    L->last = -1;
    return L;
}

result append(SeqList *L, datatype data)
{
    if (L->last + 1 >= MAXSIZE)
        return LIST_NO_SIZE;
    L->data[++(L->last)] = data;
    return SUCCESS;
}

result insert(SeqList *L, int index, datatype data)
{
    if (L->last == MAXSIZE - 1)
        return LIST_NO_SIZE;
    // insert front the element of index.
    // 1 2 3 4 5 6 [7, but available] [8, not reachable] (index)
    // 0 1 2 3 4 5 (L->last)
    // L->last=5, length=6, available indexes:[1,6], invaild index: 0, 8
    // 1<=index<=(L->last)+2 (1 offset between index and last + 1 border checking offset)
    if (index < 1 || index > L->last + 2)
        return WRONG_INDEX;
    // before: 0 1 2 3 4 5 6
    // after : 0 1 2 3 _ 4 5 6
    //                 -->
    for (int i = L->last; i >= index - 1; i--)
        L->data[i + 1] = L->data[i];
    L->last++;
    L->data[index - 1] = data;
    return SUCCESS;
}

result erase(SeqList *L, int index)
{
    // 1 2 3 4 5 6 (index)
    // 0 1 2 3 4 5 (L->last)
    //       ^ delete_index = 4, L->last = 3
    //       <--
    // 0 1 2 4 5
    // for i in [4(index),5(L->last)]:
    //     L->data[i-1](3) = L->data[i](4)
    if (index < 1 || L->last + 1 < index)
        return WRONG_INDEX;
    for (int i = index; i <= L->last; i++) // index already plus 1 caused by offset between index and L->last
        L->data[i - 1] = L->data[i];
    L->last--;
    return SUCCESS;
}

int location(SeqList *L, datatype data)
{
    for (int i = 0; i < L->last; i++)
        if (L->data[i] == data)
            return i;
    return NO_RESULT;
}

SeqList *merge(SeqList *A, SeqList *B)
{
    int pa = 0, pb = 0, pc = 0;
    SeqList *R = init();
    // 0 1 2 3 4 5 (pa, A->last+1)
    // 1 2 3 4 5 6 (A->last)
    while (A->last >= pa && B->last >= pb)
        if (A->data[pa] < B->data[pb])
            R->data[pc++] = A->data[pa++];
        else
            R->data[pc++] = B->data[pb++];
    while (A->last >= pa)
        R->data[pc++] = A->data[pa++];
    while (B->last >= pb)
        R->data[pc++] = B->data[pb++];
    R->last = pc - 1;
    return R;
}

void print(SeqList *L)
{
    for (int i = 0; i <= L->last; i++)
        printf("%d ", L->data[i]);
    printf("\n");
}

#pragma endregion

int main()
{
    SeqList *seqlist = init();
    for (int i = 0; i < 10; i++)
        append(seqlist, rand() % 20);
    int x = 4, y = 10, offset = 0;
    print(seqlist);
    SeqList *offsetList = init();
    for (int i = 0; i <= seqlist->last; ++i)
    {
        if (x <= seqlist->data[i] && seqlist->data[i] <= y)
            offset++;
        else
            seqlist->data[i - offset] = seqlist->data[i];
    }
    seqlist->last -= offset;
    print(seqlist);
    return 0;
}

// remove the value in interval [x,y] (x<=y)
int main2()
{
    SeqList *seqlist = init();
    for (int i = 0; i < 10; i++)
        append(seqlist, rand() % 20);
    int x = 4, y = 10;
    print(seqlist);
    // range: [2,3]
    // 1 2 1 5 1 3 1 6
    // x v x x x v x x (isInRange)
    // 0 - 1 1 1 - 2 2 (offset)
    // 1 1 5 1 1 3 1 6 (doOffset(1))
    // 1 1 5 1 1 6 1 6 (doOffset(2))
    // 1 1 5 1 1 6
    int offset = 0, j;
    SeqList *offsetList = init();
    for (int i = 0; i <= seqlist->last; ++i)
    {
        if (x <= seqlist->data[i] && seqlist->data[i] <= y)
        {
            append(offsetList, -1);
            offset++;
        }
        else
            append(offsetList, offset);
    }

    for (j = 0; j <= offsetList->last; ++j)
    {
        if (offsetList->data[j] == -1)
            continue;
        seqlist->data[j - offsetList->data[j]] = seqlist->data[j];
    }
    seqlist->last -= offset;
    print(seqlist);
    return 0;
}