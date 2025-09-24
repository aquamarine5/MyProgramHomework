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

typedef struct
{
    datatype data[MAXSIZE];
    int last;
} SeqList;

SeqList *init()
{
    SeqList *L = (SeqList *)malloc(sizeof(SeqList));
    L->last = -1;
}

result insert(SeqList *L, int index, datatype data)
{
    if (L->last == MAXSIZE - 1)
        return LIST_NO_SIZE;
    // insert front the element of index.
    // 1 2 3 4 5 6 [7, but available] [8, not reachable] (index)
    // 0 1 2 3 4 5 (L->last)
    // L->last=5, length=6, available indexes:[1,6], invaild index: 0, 8
    // 1<=index<=(L->last)+1
    if (index < 1 || index > L->last + 2)
        return WRONG_INDEX;
    // before: 0 1 2 3 4 5 6
    // after : 0 1 2 3 _ 4 5 6
    //                 -->
    for (int i = L->last; i >= index; i--)
        L->data[i + 1] = L->data[i];
    L->last++;
    L->data[index - 1] = data;
    return SUCCESS;
}

result delete(SeqList *L, int index)
{
    // 1 2 3 4 5 6 (index)
    // 0 1 2 3 4 5 (L->last)
    //       ^ delete_index
    //       <--
    // 0 1 2 4 5
    if (index < 1 || L->last + 1 < index)
        return WRONG_INDEX;
    for (int i = index + 1; i < L->last - 1; i++)
        L->data[i + 1] = L->data[i];
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
    for (int i = 0; i < L->last; i++)
        printf("%d ", L->data[i]);
}