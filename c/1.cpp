#include <iostream>
using namespace std;
int f(int a)
{
    auto b = 0;
    static int c = 3;
    b += 1;
    c += 1;
    return a + b + c;
}
int main()
{
    int a = 2, i;
    for (i = 0; i < 3; ++i)
    {
        cout << f(a) << endl;
    }
}