/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
 */
#include <iostream>
#include <vector>
#include <algorithm>
#include <map>
using namespace std;
bool isdebug = 1;
long long cl(vector<int> n)
{
    int a = 0;
    for (int i = 0; i < n.size(); i++)
    {
        a += n[i];
    }
    return a;
}
int main()
{
    int t;
    cin >> t;
    while (t--)
    {
        int l;
        cin >> l;
        if (l == 1)
        {
            int k;
            cin >> k;
            if (k == 0)
            {
                cout << 1 << endl;
            }
            else
            {
                cout << 0 << endl;
            }
            continue;
        }
        vector<int> a(l);
        for (int i = 0; i < l; i++)
        {
            cin >> a[i];
        }
        map<long long, bool> mp;
        mp[0] = true;
        long long s = 0;
        int ans = 0;
        for (int i = 1; i <= l; i++)
        {
            s += a[i];
            mp[a[i] * 2] = true;
            if (mp.count(s))
                ans++;
        }
        cout << ans << endl;
    }
}