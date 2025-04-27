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
void rightShiftArray(int a[], int n, int digit)
{
    int b[100];
    for (int i = n - digit; i < n; ++i)
    {
        b[i - n + digit] = a[i];
    }
    for (int j = 0; j < n - digit; ++j)
    {
        swap(&a[j], &a[j + digit]);
    }
    for (int k = 0; k < digit; ++k)
    {
        a[k] = b[k];
    }
}
// 1 2 3 4 5 6
// 2
// 5 6 1 2 3 4
int main()
{
    int a[100], n, digit;
    printf("Please input the number of elements in the array: ");
    scanf("%d", &n);
    printf("Please input the elements of the array:\n");
    inputArray(a, n);
    scanf("%d", &digit);
    rightShiftArray(a, n, digit);
    printf("The array after right shift is:\n");
    outputArray(a, n);
}
