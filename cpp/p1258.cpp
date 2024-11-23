#include <iostream>
#include <vector>
using namespace std;
int main()
{
    double s, a, b;
    cin >> s >> a >> b;
    double x = (2 * a * s) / (3 * a + b);
    // human walked x meters
    // -x- -s-2x- -x-
    printf("%.6f", x / a + (s - x) / b);
}