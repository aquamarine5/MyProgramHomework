/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
 */
#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
bool judge(int lp, int rp, int l, int n, int m, int mid, vector<int> a)
{
    int tot = 0, nowp = 0;
    for (int i = 1; i <= n + 1; ++i)
    {
        if (a[i] - a[nowp] < mid)
        {
            tot++;
        }
        else
            nowp = i;
    }
    return tot <= m;
}
int main()
{
    int l, n, m;
    cin >> l >> n >> m;
    vector<int> a(n + 10);
    for (int i = 1; i <= n; i++)
    {
        cin >> a[i];
    }
    a[n + 1] = l;
    int lp = 1, rp = l, mid;
    while (lp < rp)
    {
        mid = (lp + rp) / 2;
        if (judge(lp, rp, l, n, m, mid, a))
        {
            lp = mid + 1;
        }
        else
            rp = mid;
    }
    cout << lp - 1 << endl;
}