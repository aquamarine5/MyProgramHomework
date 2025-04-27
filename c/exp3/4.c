#include <stdio.h>
void inputArray(int a[], int *n)
{
    for (int i = 0; i < *n; ++i)
    {
        scanf("%d", &a[i]);
    }
}
void outputArray(int a[], int *n)
{
    for (int i = 0; i < *n; i++)
    {
        printf("%d ", a[i]);
    }
}
void deleteElement(int a[], int value, int *n)
{
    int index = 0;
    for (int i = 0; i < *n; i++)
    {
        if (a[i] != value)
        {
            a[index++] = a[i];
        }
    }
    (*n) = index;
}
int main()
{
    int a[100], n, value;
    printf("Please input the number of elements in the array: ");
    scanf("%d", &n);
    printf("Please input the elements of the array:\n");
    inputArray(a, &n);
    printf("Please input the value to be deleted:\n");
    scanf("%d", &value);
    deleteElement(a, value, &n);
    printf("Length of the array after deletion: %d\n", n);
    printf("The array after deletion is:\n");
    outputArray(a, &n);
}