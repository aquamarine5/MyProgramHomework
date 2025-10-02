#include <stdio.h>
#include <stdlib.h>

typedef struct LNode
{
    int data;
    struct LNode *next;
} LNode, *LinkList;

void Create_LinkList(LinkList *L, int n)
{
    *L = (LinkList)malloc(sizeof(LNode));
    (*L)->next = NULL;
    LNode *tail = *L;
    for (int i = 0; i < n; ++i)
    {
        LNode *p = (LNode *)malloc(sizeof(LNode));
        p->next = NULL;
        scanf("%d", &p->data);
        tail->next = p;
        tail = p;
    }
}

void print_LinkList(LinkList L)
{
    LNode *p = L->next;
    while (p)
    {
        printf("%d", p->data);
        p = p->next;
    }
}

void ListDelete_LSameNode(LinkList L)
{
    // 删除链表中重复元素
    // 请在此处编写代码

    LNode *node = L->next, *iter, *temp;
    while (node->next)
    {
        iter = node;
        while (iter->next)
        {
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            // iter    i.nx
            // node.data != i.nx.data (@tips: i.nx=iter.next)

            // $$ next $$
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            //         iter    i.nx           (iter = iter->next;)
            // node.data == i.nx.data

            // $$ executed `if` $$            (if(node->data == iter->next->data))
            // [1.] -> [2.] -> [1.] -> [5.]
            // node
            //         iter    i.nx
            //                 temp           (temp = iter->next;)

            //          /---------------\
            //          |               ↓
            // [1.] -> [2.]    x__x -> [5.]   (iter->next = temp->next;)
            // node
            //         iter    i.nx
            //                 temp    t.nx   (free(temp);)
            if (node->data == iter->next->data)
            {
                temp = iter->next;
                iter->next = temp->next;
                free(temp);
            }
            else
            {
                iter = iter->next;
            }
        }
        if (node->next == NULL)
        {
            break;
        }
        node = node->next;
    }
}

int main()
{
    // 创建链表
    LinkList L;

    // 输入数据
    int count;
    printf("请输入链表的元素个数：");
    scanf("%d", &count);
    printf("请输入链表的数据：\n");
    Create_LinkList(&L, count);
    ListDelete_LSameNode(L);
    printf("删除相关元素后的链表为：");
    print_LinkList(L);

    return 0;
}