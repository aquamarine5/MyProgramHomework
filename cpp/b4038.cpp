#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;

int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int n;
        cin >> n;
        vector<int> a(n + 1);
        for (int i = 1; i <= n; ++i)
        {
            cin >> a[i];
        }

        int s = 0;
        for (int i = 1; i <= n; ++i)
        {
            s += a[i];
        }
        int sum = 0;
        int r = 0;
        for (int i = 1; i < n; ++i)
        {
            sum += a[i];
            if (s == sum * 2)
            {
                r = 1;
            }
        }
        if (r)
        {
            cout << "Yes" << endl;
        }
        else
        {
            cout << "No" << endl;
        }
    }
    return 0;
}
// * 1 2 3
// * 1 3 6 j=1 a=3 1/5
// * 1 3 6 j=2 a=3 3/
// * 2 3 1 4
// * 2 5 6 10 j=2 a=4
// 0 1 2 3 4