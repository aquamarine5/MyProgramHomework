#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int n, m;
    scanf("%d%d", &n, &m);
    vector<int> nx(n + 1);
    for (int i = 1; i <= n; ++i)
    {
        int x;
        cin >> nx[i];
    }

    while (m--)
    {
        int x;
        int l = 1, r = n;
        cin >> x;
        while (l < r)
        {
            int mid = (l + r) / 2;
            if (nx[mid] < x)
                l = mid + 1;
            else
                r = mid;
        }
        if (nx[l] == x)
            cout << l << " ";
        else
            cout << -1 << " ";
    }
}