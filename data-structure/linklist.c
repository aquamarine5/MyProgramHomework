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

typedef LinkList LinkListWithTail;

// head is blank data
// [_blank] -> NULL -or- [datatype] -> [datetype]
LinkListWithTail init()
{
    LinkList L = (LinkList)malloc(sizeof(LinkNode));
    L->next = NULL;
    return L;
}

void insertAtTail(LinkNode *L, datatype data)
{
    LinkNode *node = (LinkNode *)malloc(sizeof(LinkNode));
    node->data = data;
    node->next = NULL;
    L->next = node;
}

// create at tail
// head without data
LinkListWithTail createInOrder()
{
    datatype value;
    LinkListWithTail L = init();
    LinkNode *tail = L->next;
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

int length(LinkList L)
{
    int i = 0;
    LinkNode *node = L;
    while (node != NULL)
    {
        node = node->next;
        i++;
    }
    return i;
}
LinkNode *get(LinkListWithTail L, int index)
{
    LinkNode *node = L->next;
    for (int i = 1; i < index; i++)
    {
        if (node->next == NULL)
            return NULL;
    }
    return node->next;
}
LinkNode *locate(LinkList L, datatype data)
{
    LinkNode *node = L;
    while (node->next != NULL)
    {
        if (node->data == data)
            return node;
        else
            node = node->next;
        return NO_RESULT;
    }
}

LinkNode *locate(LinkListWithTail L, datatype data)
{
    LinkNode *node = L->next;
    while (node != NULL)
        if (node->data == data)
            return node;
        else
            node = node->next;
    return NO_RESULT;
}

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

result delete(LinkListWithTail L, int index)
{
    int i = 1;
    LinkNode *node = L->next, *temp;
    while (node->next != NULL)
    {
        // [i-1] -> [i] -> [i+1]
        // [i-1] -> [i+1]
        if (i == index - 1)
        {
            temp = node->next;
            if (temp == NULL)
                return WRONG_INDEX;
            node->next = temp->next;
            free(temp);
            return SUCCESS;
        }
        else
            i++;
    }
    if (i < index)
        return WRONG_INDEX;
}

void reverse(LinkListWithTail L)
{
    LinkNode *node = L->next, *temp;
    // [head] -> [node] -> [2] -> [3] -> [4]
    L->next = NULL;
    // [head] -> NULL
    // [head] -> [temp]
    // [head] -> [node] -> [temp]
    while (node->next != NULL)
    {
        temp = L->next;
        L->next = node;
        node->next = temp;
        node = node->next;
    }
}

void deduplication(LinkListWithTail L)
{
    LinkNode *node = L->next, *iter, *temp;
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
