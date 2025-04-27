#include <stdio.h>
void inputMatrix(int matrix[][100], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            scanf("%d", &matrix[i][j]);
        }
    }
}
void outputMatrix(int matrix[][100], int n)
{
    for (int i = 0; i < n; i++)
    {
        for (int j = 0; j < n; j++)
        {
            printf("%d ", matrix[i][j]);
        }
        printf("\n");
    }
}
int sumDiagonals(int matrix[][100], int n)
{
    int sum = 0;
    for (int i = 0; i < n; i++)
    {
        sum += matrix[i][i];
    }
    for (int i = 0; i < n; i++)
    {
        if (n % 2 == 1 && i == n / 2)
        {
            continue;
        }
        sum += matrix[i][n - 1 - i];
    }
    return sum;
}
int main()
{
    int n;
    printf("Enter the size of the matrix: ");
    scanf("%d", &n);
    int matrix[100][100];
    printf("Enter the elements of the matrix:\n");
    inputMatrix(matrix, n);
    printf("The matrix is:\n");
    outputMatrix(matrix, n);
    int sum = sumDiagonals(matrix, n);
    printf("Sum of diagonals: %d\n", sum);
    return 0;
}