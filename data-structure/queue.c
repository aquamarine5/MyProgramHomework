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

typedef struct Queue
{
    datatype data;
    struct Queue *next;
} Queue, *LinkQueue;

typedef struct
{
    // LinkQueue head=rear->next;
    LinkQueue rear;
    int length;
} SeqQueue;

typedef SeqQueue SqQueue;

SeqQueue *init()
{
    SeqQueue *value = (SeqQueue *)malloc(sizeof(SeqQueue));
    value->length = 0;
    value->rear = NULL;
    return value;
}

bool isEmpty(SeqQueue *queue)
{
    return queue->length == 0;
}

void enqueue(SeqQueue *queue, datatype data)
{
    Queue *node = (Queue *)malloc(sizeof(Queue));
    node->data = data;
    if (isEmpty(queue))
    {
        node->next = node;
        queue->rear = node;
    }
    else
    {
        node->next = queue->rear->next;
        queue->rear->next = node;
        queue->rear = node;
    }
    queue->length++;
}

void dequeue(SeqQueue *queue, datatype *data)
{
    if (isEmpty(queue))
    {
        *data = NO_RESULT;
        return;
    }
    Queue *front = queue->rear->next;
    *data = front->data;
    if (queue->rear == front)
        queue->rear = NULL;
    else
        queue->rear->next = front->next;
    free(front);
    queue->length--;
}

int main()
{
    SeqQueue *queue = init();
    for (int i = 1; i <= 9; i++)
    {
        enqueue(queue, i);
    }
    int buffer;
    while (!isEmpty(queue))
    {
        dequeue(queue, &buffer);
        printf("%d ", buffer);
    }
    return 0;
}