#include <stdio.h>
inline int abs(int x)
{
    return x < 0 ? -x : x;
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
float averageArray(int a[], int n)
{
    float sum = 0;
    for (int i = 0; i < n; ++i)
    {
        sum += a[i];
    }
    return sum / n;
}
int closestValue(int a[], int n, float value)
{
    int closest = a[0];
    int minDiff = abs(a[0] - value);
    for (int i = 1; i < n; i++)
    {
        int diff = abs(a[i] - value);
        if (diff < minDiff)
        {
            minDiff = diff;
            closest = a[i];
        }
    }
    return closest;
}
main()
{
    int n;
    scanf("%d", &n);
    int a[100];
    inputArray(a, n);
    printf("\n");
    float avg = averageArray(a, n);
    printf("Average: %.2f\n", avg);
    int closest = closestValue(a, n, avg);
    printf("Closest value to average: %d\n", closest);
}