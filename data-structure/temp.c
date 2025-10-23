#include <stdio.h>
#include <stdlib.h>

typedef int ElemType;
typedef struct queue
{
    ElemType data;
    struct queue *next;
} queue, *LinkQueue;
typedef struct
{
    LinkQueue rear;
    int length;
} SqQueue;

void InitQueue(SqQueue *queue)
{
    // 初始化队列，空队列
    // 请在此处编写代码
    queue->length = 0;
    queue->rear = NULL;
}

int EmptyQueue(SqQueue *queue)
{
    // 判空操作
    // 请在此处编写代码
    return queue->length == 0;
}

void EnQueue(SqQueue *queue, ElemType data)
{
    LinkQueue node = (LinkQueue)malloc(sizeof(struct queue));
    node->data = data;
    if (EmptyQueue(queue))
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

void DelQueue(SqQueue *queue, ElemType *data)
{
    if (EmptyQueue(queue))
    {
        return;
    }
    LinkQueue front = queue->rear->next;
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
    int x, n;
    SqQueue Q;
    ElemType elem;
    InitQueue(&Q);

    // 判断队列是否为空
    if (EmptyQueue(&Q))
        printf("目前是一个空队列！\n");
    else
        printf("目前该队列中有元素，不为空！\n");

    // 入队
    printf("输入入队元素个数：");
    scanf("%d", &n);
    for (int i = 1; i <= n; i++)
    {
        printf("输入第%d个入队元素：", i);
        scanf("%d", &x);
        EnQueue(&Q, x);
    }

    printf("出队元素：");
    // 出队
    for (int j = 1; j <= n; j++)
    {
        DelQueue(&Q, &elem);
        printf("%d", elem);
    }
    return 0;
}
