/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2025 by @aquamarine5, RC. All Rights Reversed.
 */
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#pragma region SeqStack

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
result popIgnoreReturn(SeqStack *s)
{
    if (isEmpty(s))
        return WRONG_INDEX;
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
#pragma endregion
#define priority int

priority getPriorityInStack(char op)
{
    switch (op)
    {
    case '^':
        return 3;
    case '*':
    case '/':
    case '%':
        return 2;
    case '+':
    case '-':
        return 1;
    case '(':
        return 0;
    case ')':
        return -1;
    default:
    {
        printf("Invaild operator[%c]", op);
        return WRONG_INDEX;
        break;
    }
    }
}
priority getPriorityOutStack(char op)
{
    switch (op)
    {
    case '^':
        return 4;
    case '*':
    case '/':
    case '%':
        return 2;
    case '+':
    case '-':
        return 1;
    case '(':
        return 4;
    case ')':
        return -1;
    default:
    {
        printf("Invaild operator[%c]", op);
        return WRONG_INDEX;
        break;
    }
    }
}
inline int execute(int num1, int num2, char op)
{
    switch (op)
    {
    case '+':
        return num2 + num1;
    case '-':
        return num2 - num1;
    case '*':
        return num2 * num1;
    case '/':
        return num2 / num1;
    case '%':
        return num2 % num1;
    case '^':
    {
        int r = 1;
        for (int i = 0; i < num1; i++)
        {
            r *= num2;
        }
        return r;
    }
    default:
        return 0;
    }
}
inline int char2int(char number)
{
    return number - '0';
}
int calculate(char s[])
{
    SeqStack *numberStack = init();
    SeqStack *operatorStack = init();
    int index = 0;
    char current = s[index];
    while (current != '\0')
    {
        if (current <= '9' && current >= '0')
        {
            push(numberStack, char2int(current));
        }
        else
        {
            if (current == ')')
            {
                int topOperator;
                top(operatorStack, &topOperator);
                while (topOperator != '(')
                {
                    int num1, num2;
                    pop(numberStack, &num1);
                    pop(numberStack, &num2);
                    popIgnoreReturn(operatorStack);
                    push(numberStack, execute(num1, num2, topOperator));
                    top(operatorStack, &topOperator);
                }
                popIgnoreReturn(operatorStack); // Pop '('
            }
            else
            {
                while (true)
                {
                    if (isEmpty(operatorStack))
                    {
                        push(operatorStack, current);
                        break;
                    }
                    int topOperator;
                    top(operatorStack, &topOperator);
                    if (getPriorityOutStack(current) > getPriorityInStack(topOperator))
                    {
                        push(operatorStack, current);
                        break;
                    }
                    else
                    {
                        if (topOperator == '(')
                        { // Don't pop '(' unless we see ')'
                            push(operatorStack, current);
                            break;
                        }
                        int num1, num2;
                        pop(numberStack, &num1);
                        pop(numberStack, &num2);
                        popIgnoreReturn(operatorStack);
                        push(numberStack, execute(num1, num2, topOperator));
                    }
                }
            }
        }
        current = s[++index];
    }

    while (!isEmpty(operatorStack))
    {
        int topOperator;
        pop(operatorStack, &topOperator);
        int num1, num2;
        pop(numberStack, &num1);
        pop(numberStack, &num2);
        push(numberStack, execute(num1, num2, topOperator));
    }

    int finalResult;
    pop(numberStack, &finalResult);
    return finalResult;
}
int main()
{
    char s[30];
    scanf("%s", s);
    printf("%d", calculate(s));
    return 0;
}