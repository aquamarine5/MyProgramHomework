#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
const char DATABASE_FILENAME[] = "students.txt";
typedef enum
{
    INPUT_STUDENT = 1,
    DISPLAY_STUDENT = 2,
    DELETE_STUDENT = 3,
    QUERY_BY_ID = 4,
    QUERY_BY_NAME = 5,
    SORT_DESCENDING = 6,
    SEARCH_FAILED = 7,
    FILE_SAVE = 8,
    FILE_LOAD = 9,
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
    float score1;
    float score2;
    float score3;
    struct Student *next;
} Student;
typedef struct
{
    Student *head;
    Student *tail;
} StudentList;
void pause()
{
    printf("\n按任意键继续...\n");
    getchar();
    getchar();
}
char *printFloat(float value)
{
    char *result = (char *)malloc(20);
    if (value == (int)value)
        sprintf(result, "%.0f", value);
    else
        sprintf(result, "%.2f", value);
    return result;
}
float totalScores(Student *student)
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
    scanf("%f %f %f", &student->score1, &student->score2, &student->score3);
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
    printf("学号: %s, 姓名: %s, 性别: %c, 成绩: %s %s %s, 总分: %s\n",
           student->id, student->name, student->gender,
           printFloat(student->score1), printFloat(student->score2), printFloat(student->score3),
           printFloat(totalScores(student)));
}
void displayStudent(StudentList *list)
{
    Student *current = list->head->next;
    if (current == NULL)
    {
        printf("没有学生信息可显示。\n");
        return;
    }
    while (current != NULL)
    {
        printStudent(current);
        current = current->next;
    }
    pause();
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
void fileSave(StudentList *list)
{
    FILE *file = fopen(DATABASE_FILENAME, "w");
    if (file == NULL)
    {
        printf("无法打开文件进行保存。\n");
        return;
    }
    Student *current = list->head->next;
    while (current != NULL)
    {
        fprintf(file, "%s %s %c %f %f %f\n",
                current->id, current->name, current->gender,
                current->score1, current->score2, current->score3);
        current = current->next;
    }
    fclose(file);

    printf("学生信息已保存到文件。\n");
}
void fileLoad(StudentList *list)
{
    FILE *file = fopen(DATABASE_FILENAME, "r");
    if (file == NULL)
    {
        printf("无法打开文件进行加载。\n");
        return;
    }
    while (!feof(file))
    {
        Student *student = (Student *)malloc(sizeof(Student));
        if (student == NULL)
        {
            printf("内存分配失败。\n");
            fclose(file);
            return;
        }
        fscanf(file, "%s %s %c %f %f %f\n",
               student->id, student->name, &student->gender,
               &student->score1, &student->score2, &student->score3);
        if (isDuplicate(list, student->id))
        {
            printf("学号 %s 已存在，跳过加载。\n", student->id);
            free(student);
            continue;
        }
        student->next = NULL;
        list->tail->next = student;
        list->tail = student;
    }
    fclose(file);

    printf("学生信息已从文件加载。\n");
}
void deleteStudent(StudentList *list)
{
    char id[20];
    printf("请输入要删除的学号: ");
    scanf("%s", id);
    Student *current = list->head;
    while (current->next != NULL)
    {
        if (strcmp(current->next->id, id) == 0)
        {
            Student *toDelete = current->next;
            current->next = toDelete->next;
            if (toDelete == list->tail)
            {
                list->tail = current;
            }
            free(toDelete);
            printf("学号为 %s 的学生信息已删除。\n", id);
            return;
        }
        current = current->next;
    }
    printf("未找到学号为 %s 的学生。\n", id);
}
STATUS launchMenu()
{
    int choice;
    printf("*************************\n");
    printf("1. 录入学生信息\n");
    printf("2. 显示学生信息\n");
    printf("3. 删除学生信息\n");
    printf("4. 按学号查找\n");
    printf("5. 按姓名查找\n");
    printf("6. 按总分递减排序\n");
    printf("7. 查找有2科目不及格的学生信息\n");
    printf("8. 保存学生信息到文件\n");
    printf("9. 从文件加载学生信息\n");
    printf("0. 退出\n");
    printf("*************************\n");
    printf("请输入您的选择: ");
    scanf("%d", &choice);
    printf("=========================\n");
    if (choice < 0 || choice > 9)
    {
        printf("无效的选择，请重新输入。\n");
        return launchMenu();
    }
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
    case DELETE_STUDENT:
        deleteStudent(studentList);
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
    case FILE_SAVE:
        fileSave(studentList);
        break;
    case FILE_LOAD:
        fileLoad(studentList);
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