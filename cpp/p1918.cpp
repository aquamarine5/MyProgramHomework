#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int n;
    cin >> n;
    vector<long long> a(n);
    for (int i = 0; i < n; i++)
    {
        cin >> a[i];
    }
    int q;
    cin >> q;
    while (q--)
    {
        long long x;
        cin >> x;
        int r = lower_bound(a.begin(), a.end(), x) - a.begin();
        if (r < n && a[r] == x)
            cout << r + 1 << endl;
        else
            cout << 0 << endl;
    }
}
// .
// ..
// ....
// ...
// .....
//  *    4