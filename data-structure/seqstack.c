/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 * lovely lonely, but be a quokka.
 */
#include <stdio.h>
#include <stdbool.h>
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
    int top;
} SeqStack;

SeqStack *init()
{
    SeqStack *s = (SeqStack *)malloc(sizeof(SeqStack));
    s->top = -1;
    return s;
}

bool isEmpty(SeqStack *s)
{
    return s->top == -1;
}

result push(SeqStack *s, datatype data)
{
    if (s->top + 1 >= MAXSIZE)
        return LIST_NO_SIZE;
    s->top++;
    s->data[s->top] = data;
    return SUCCESS;
}

result pop(SeqStack *s, datatype *data)
{
    if (isEmpty(s))
        return WRONG_INDEX;
    *data = s->data[s->top];
    s->top--;
    return SUCCESS;
}

result top(SeqStack *s, datatype *data)
{
    if (isEmpty(s))
        return WRONG_INDEX;
    *data = s->data[s->top];
    return SUCCESS;
}