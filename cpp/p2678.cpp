#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int l, n, m;
    cin >> l >> n >> m;
    for (int i = 0; i < n; i++)
    {
        int a;
        cin >> a;
        l = max(l, a);
    }
}