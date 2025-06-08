#include <stdio.h>
#include <string.h>
#include <stdlib.h>
typedef struct Node
{
    int n;
    struct Node *next;
} Node;
inline int pow(int a, int b)
{
    int result = 1;
    for (int i = 0; i < b; i++)
    {
        result *= a;
    }
    return result;
}
inline int str2int(char c[])
{
    int len = strlen(c), result = 0;
    for (int i = len - 1; i >= 0; i--)
    {
        result += pow(10, (len - i - 1)) * (c[i] - '0');
    }
    return result;
}
Node *createNode()
{
    char c[20];
    printf("Input a number('-' for stop pattern): ");
    scanf("%s", c);
    if (strcmp(c, "-") == 0)
    {
        return NULL;
    }
    Node *newNode = (Node *)malloc(sizeof(Node));
    if (newNode == NULL)
    {
        return NULL;
    }
    newNode->n = str2int(c);
    newNode->next = NULL;
    return newNode;
}
inline Node *createHead()
{
    Node *head = (Node *)malloc(sizeof(Node));
    if (head == NULL)
    {
        return NULL;
    }
    head->next = NULL;
    return head;
}
void inputNode(Node *head)
{
    Node *current = head;
    while (1)
    {
        Node *newNode = createNode();
        if (newNode == NULL)
        {
            break;
        }
        current->next = newNode;
        current = current->next;
    }
}
void findMax(Node *head)
{
    if (head == NULL || head->next == NULL)
    {
        printf("No nodes to compare.\n");
        return;
    }
    Node *current = head->next;
    int max = current->n;
    while (current != NULL)
    {
        if (current->n > max)
        {
            max = current->n;
        }
        current = current->next;
    }
    printf("The maximum value is: %d\n", max);
}
void freeAllNode(Node *head)
{
    Node *buffer;
    while (buffer != NULL)
    {
        buffer = head;
        head = buffer->next;
        free(buffer);
    }
}
int main()
{
    Node *head = createHead();
    inputNode(head);
    findMax(head);
    freeAllNode(head);
}
