#include<stdio.h>
#include<stdlib.h>
#include<string.h>
typedef struct Node{
    int id;
    char name[20];
    struct Node* next;
} Node;

Node* createHead(){
    Node *head=(Node*)malloc(sizeof(Node));
    head->next=NULL;
    return head;
}

void insert1(Node* head){
    Node *tail=head,*temp;
    while(1){
        temp=(Node*)malloc(sizeof(Node));
        scanf("%d %s",&temp->id,temp->name);
        if(strcmp(temp->name,"x")==0){
            free(temp);
            break;
        }

        temp->next=NULL;
        tail->next=temp;
        tail=temp;
    }
}

void insert2(Node* head){
    Node *tail=head,*temp;
    int n;
    scanf("%d",&n);
    for(int i=0;i<n;i++){
        temp=(Node*)malloc(sizeof(Node));
        scanf("%d %s",&temp->id,temp->name);

        temp->next=NULL;
        tail->next=temp;
        tail=temp;
    }
}