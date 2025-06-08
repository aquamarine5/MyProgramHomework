#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
typedef enum
{
    INPUT_STUDENT = 1,
    DISPLAY_STUDENT = 2,
    QUERY_BY_ID = 3,
    QUERY_BY_NAME = 4,
    SORT_DESCENDING = 5,
    SEARCH_FAILED = 6,
    EXIT = 0
} STATUS;
typedef enum
{
    MALE = 'M',
    FEMALE = 'F'
} GENDER;
typedef struct Student
{
    char id[20];
    char name[20];
    GENDER gender;
    int score1;
    int score2;
    int score3;
    struct Student *next;
} Student;
typedef struct
{
    Student *head;
    Student *tail;
} StudentList;
int totalScores(Student *student)
{
    return student->score1 + student->score2 + student->score3;
}

bool isDuplicate(StudentList *list, char id[])
{
    Student *current = list->head;
    while (current != NULL)
    {
        if (strcmp(current->id, id) == 0)
        {
            return true;
        }
        current = current->next;
    }
    return false;
}

void inputStudent(StudentList *list)
{
    Student *student = (Student *)malloc(sizeof(Student));
    if (student == NULL)
    {
        return;
    }
    char stuid[20], gender;
    printf("请输入学号: ");
    scanf("%s", &stuid);
    if (strcmp(stuid, "x") == 0)
    {
        free(student);
        return;
    }
    else if (isDuplicate(list, stuid))
    {
        printf("学号已存在，请重新输入。\n");
        free(student);
        return;
    }
    strcpy(student->id, stuid);
    printf("请输入姓名: ");
    scanf("%s", student->name);
    printf("请输入性别 (M/F): ");
    scanf(" %c", &gender);
    if (gender == 'M')
    {
        student->gender = MALE;
    }
    else if (gender == 'F')
    {
        student->gender = FEMALE;
    }
    else
    {
        printf("无效的性别输入。\n");
        free(student);
        return;
    }
    printf("请输入三门课的成绩(以空格分隔): ");
    scanf("%d %d %d", &student->score1, &student->score2, &student->score3);
    student->next = NULL;
    list->tail->next = student;
    list->tail = student;
}
StudentList *createStudentList()
{
    StudentList *list = (StudentList *)malloc(sizeof(StudentList));
    if (list == NULL)
    {
        return NULL;
    }
    list->head = (Student *)malloc(sizeof(Student));
    if (list->head == NULL)
    {
        free(list);
        return NULL;
    }
    list->head->next = NULL;
    list->tail = list->head;
    return list;
}
void freeStudentList(StudentList *list)
{
    Student *current = list->head;
    while (current != NULL)
    {
        Student *temp = current;
        current = current->next;
        free(temp);
    }
    free(list);
}
void printStudent(Student *student)
{
    printf("学号: %s, 姓名: %s, 性别: %c, 成绩: %d %d %d, 总分: %d\n",
           student->id, student->name, student->gender,
           student->score1, student->score2, student->score3,
           totalScores(student));
}
void displayStudent(StudentList *list)
{
    Student *current = list->head->next;
    while (current != NULL)
    {
        printStudent(current);
        current = current->next;
    }
}
void queryById(StudentList *list)
{
    char id[20];
    printf("请输入学号: ");
    scanf("%s", id);
    Student *current = list->head->next;
    bool isfound = false;
    while (current != NULL)
    {
        if (strcmp(current->id, id) == 0)
        {
            printStudent(current);
            isfound = true;
        }
        current = current->next;
    }
    if (!isfound)
    {
        printf("未找到学号为 %s 的学生。\n", id);
    }
}

void queryByName(StudentList *list)
{
    char name[20];
    printf("请输入姓名: ");
    scanf("%s", name);
    Student *current = list->head->next;
    bool isfound = false;
    while (current != NULL)
    {
        if (strcmp(current->name, name) == 0)
        {
            printStudent(current);
            isfound = true;
        }
        current = current->next;
    }
    if (!isfound)
    {
        printf("未找到姓名为 %s 的学生。\n", name);
    }
}
void sortDescendingByScore(StudentList *list)
{
    if (list->head->next == NULL || list->head->next->next == NULL)
    {
        printf("学生信息不足，无法排序。\n");
        return;
    }
    bool isDescending;
    while (!isDescending)
    {
        isDescending = true;
        Student *current = list->head->next;
        while (current->next != NULL)
        {
            if (totalScores(current) < totalScores(current->next))
            {
                // 交换节点数据
                Student temp = *current;
                *current = *current->next;
                *current->next = temp;
                current->next->next = current->next;
                isDescending = false;
            }
            current = current->next;
        }
    }
    displayStudent(list);
}
void searchFailedStudents(StudentList *list)
{
    Student *current = list->head->next;
    int failedCount = 0;
    bool found = false;
    while (current != NULL)
    {
        if (current->score1 < 60)
        {
            failedCount++;
        }
        if (current->score2 < 60)
        {
            failedCount++;
        }
        if (current->score3 < 60)
        {
            failedCount++;
        }
        if (failedCount >= 2)
        {
            printStudent(current);
            found = true;
        }
        current = current->next;
        failedCount = 0;
    }
    if (!found)
    {
        printf("没有找到有两科目不及格的学生。\n");
    }
}
STATUS launchMenu()
{
    int choice;
    printf("*************************\n");
    printf("1. 录入学生信息\n");
    printf("2. 显示学生信息\n");
    printf("3. 按学号查找\n");
    printf("4. 按姓名查找\n");
    printf("5. 按总分递减排序\n");
    printf("6. 查找有2科目不及格的学生信息\n");
    printf("0. 退出\n");
    printf("*************************\n");
    printf("请输入您的选择: ");
    scanf("%d", &choice);
    return (STATUS)choice;
}
void launchAction(STATUS status, StudentList *studentList)
{
    printf("\n");
    switch (status)
    {
    case INPUT_STUDENT:
        inputStudent(studentList);
        break;
    case DISPLAY_STUDENT:
        displayStudent(studentList);
        break;
    case QUERY_BY_ID:
        queryById(studentList);
        break;
    case QUERY_BY_NAME:
        queryByName(studentList);
        break;
    case SORT_DESCENDING:
        sortDescendingByScore(studentList);
        break;
    case SEARCH_FAILED:
        searchFailedStudents(studentList);
        break;
    case EXIT:
        printf("退出程序。\n");
        return;
    }
    launchAction(launchMenu(), studentList);
}
main()
{
    StudentList *studentList = createStudentList();
    if (studentList == NULL)
    {
        printf("内存分配失败。\n");
        return EXIT_FAILURE;
    }
    launchAction(launchMenu(), studentList);
    freeStudentList(studentList);
}