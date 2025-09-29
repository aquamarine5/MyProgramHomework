/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
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

typedef struct DoublyLinkNode
{
    datatype data;
    struct DoublyLinkNode *prev, *next;
} DoublyLinkNode;

typedef DoublyLinkNode *DoublyLinkList;
