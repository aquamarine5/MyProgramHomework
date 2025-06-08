#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef struct Node
{
    int data;
    char name[20];
    struct Node *next;
} Node;
typedef struct LinkedList
{
    Node *head;
    Node *tail;
} LinkedList;

Node *createNode()
{
    Node *newNode = (Node *)malloc(sizeof(Node));
    if (newNode == NULL)
    {
        return NULL;
    }
    scanf("%s %d", newNode->name, &newNode->data);
    if (strcmp(newNode->name, "-") == 0)
    {
        free(newNode);
        return NULL;
    }
    newNode->next = NULL;
    return newNode;
}

void inputNode(Node *head)
{
    Node *temp;
    while (1)
    {
        temp = createNode();
        if (temp == NULL)
        {
            break;
        }
        temp->next = head->next;
        head->next = temp;
    }
}

void inputNode(){
    Node *head = createNode();
    Node *temp;
    while (1)
    {
        temp = createNode();
        if (temp == NULL)
        {
            break;
        }
        temp->next = head->next;
        head->next = temp;
    }
}

void printNode(LinkedList list)
{
    Node *temp = list.head;
    while (temp != NULL)
    {
        printf("%s %d\n", temp->name, temp->data);
        temp = temp->next;
    }
}

void printNode(Node *head)
{
    Node *temp = head;
    while (temp != NULL)
    {
        printf("%s %d\n", temp->name, temp->data);
        temp = temp->next;
    }
}

LinkedList inputNodeWithTail(Node *head)
{
    Node *temp, *tail;
    LinkedList list;
    tail = head;
    while (1)
    {
        temp = createNode();
        if (temp == NULL)
        {
            break;
        }
        tail->next = temp;
        tail = temp;
    }
    list.head = head;
    list.tail = tail;
    return list;
}

void freeAllNode(Node *head)
{
    Node *temp;
    while (head != NULL)
    {
        temp = head;
        head = head->next;
        free(temp);
    }
}

void insertNode(Node *head, Node *value, int index)
{
    int i = 0;
    Node *temp = head;
    while (i < index - 1)
    {
        if (temp == NULL)
        {
            printf("index out of range\n");
            return;
        }
        temp = temp->next;
        i++;
    }
    value->next = temp->next;
    temp->next = value;
}

void deleteNode(Node *head, int index)
{
    int i = 0;
    Node *temp = head;
    while (i < index - 1)
    {
        if (temp == NULL)
        {
            printf("index out of range\n");
            return;
        }
        if (i == index)
        {
            Node *deleteNode = temp->next;
            temp->next = deleteNode->next;
            free(deleteNode);
            return;
        }
        temp = temp->next;
        i++;
    }
}

main()
{
    Node *head = createNode();
    LinkedList list = inputNodeWithTail(head);
    printNode(list);
    freeAllNode(list.head);
}