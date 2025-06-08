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
    char s[] = "sitts";
    void *p;
    p = s;
    printf("%d\n", *s);
}