#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int n, k;
    cin >> n >> k;
    vector<int> a(n);
    for (int i = 0; i < n; i++)
    {
        cin >> a[i];
    }
    sort(a.begin(), a.end());
    int l = 0, r = 1e9;
    while (l + 1 < r)
    {
        int mid = (l + r) / 2;
        int count = 0;
        for (int i = 0; i < n; i++)
        {
            count += a[i] / mid;
        }
        if (count >= k)
        {
            l = mid;
        }
        else
        {
            r = mid;
        }
    }
    cout << l << endl;
}