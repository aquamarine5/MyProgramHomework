#include <stdio.h>
void swap(int *a, int *b)
{
    int temp = *a;
    *a = *b;
    *b = temp;
}
void inputArray(int a[], int n)
{
    for (int i = 0; i < n; ++i)
    {
        scanf("%d", &a[i]);
    }
}
void outputArray(int a[], int n)
{
    for (int i = 0; i < n; i++)
    {
        printf("%d ", a[i]);
    }
}
void rightShiftArray(int a[], int n)
{
    for (int i = n - 1; i > 0; i--)
    {
        swap(&a[i], &a[i - 1]);
    }
}
int main()
{
    int a[100], n;
    printf("Please input the number of elements in the array:\n");
    scanf("%d", &n);
    printf("Please input the elements of the array:\n");
    inputArray(a, n);
    rightShiftArray(a, n);
    printf("The array after right shift is:\n");
    outputArray(a, n);
}
