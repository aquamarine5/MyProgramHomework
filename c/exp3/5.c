#include <stdio.h>
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
float averageArray(int a[], int n)
{
    float sum = 0;
    for (int i = 0; i < n; ++i)
    {
        sum += a[i];
    }
    return sum / n;
}
void rearrangeArray(int a[], int n, float average)
{
    int b[100], index = 0, iindex = 0;
    for (int i = 0; i < n; ++i)
    {
        if (a[i] <= average)
        {
            b[index++] = a[i];
        }
        else
        {
            a[iindex++] = a[i];
        }
    }
    for (int j = 0; j < index; ++j)
    {
        a[j + iindex] = b[j];
    }
}
main()
{
    int a[100], n;
    printf("Please input the number of elements in the array: ");
    scanf("%d", &n);
    printf("Please input the elements of the array:\n");
    inputArray(a, n);
    float average = averageArray(a, n);
    rearrangeArray(a, n, average);
    printf("The average of the array is: %.1f\n", average);
    printf("The array after rearrangement is:\n");
    outputArray(a, n);
}