#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int k, x;
    for (k = 1, x = 0; k < 5; x += 3 * k++)
    {
        k++;
    }
    printf("%d\n", x); // 输出x的值
    return 0;
}
