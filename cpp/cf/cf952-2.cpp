/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
 */
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
        int n, ans = -1, v = -1;
        cin >> n;
        for (int i = 2; i <= n; ++i)
        {
            int cp = 1, cv = 0;
            while (i * cp <= n)
            {
                cp++;
                cv += (i) * (cp - 1);
                // cout << cv << " " << cp << endl;
            }
            // cout << cv << " " << cp << endl;
            if (cv > ans)
            {
                ans = cv;
                v = i;
            }
        }
        cout << v << endl;
    }
}