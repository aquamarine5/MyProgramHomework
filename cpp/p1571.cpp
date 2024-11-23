#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int n, m;
    cin >> n >> m;
    vector<int> np(100010, 0), mp(100010, 0);
    for (int i = 1; i <= n; i++)
    {
        cin >> np[i];
    }
    for (int i = 1; i <= m; i++)
    {
        cin >> mp[i];
    }
    sort(mp.begin(), mp.begin() + m + 1);
    for (int i = 1; i <= n; ++i)
    {
        if (binary_search(mp.begin(), mp.begin() + m + 1, np[i]))
        {
            cout << np[i] << " ";
        }
        // int id = np[i];
        // int lp = 0, rp = m;
        // while (lp < rp)
        // {
        //     int mid = (lp + rp) / 2;
        //     if (mp[mid] < id)
        //     {
        //         lp = mid + 1;
        //     }
        //     else
        //     {
        //         rp = mid;
        //     }
        //     if (mp[lp] == id)
        //     {
        //         cout << id << " ";
        //         break;
        //     }
        // }
    }
}