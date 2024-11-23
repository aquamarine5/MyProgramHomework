#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int n, w, maxp = 0;
    cin >> n >> w;
    long long sumx[100010];
    sumx[0] = 0;
    vector<int> dp(100010, 0);
    for (int i = 1; i <= n; ++i)
    {
        int p, lc;
        cin >> p;
        maxp = max(maxp, p);
        cin >> lc;
        dp[p] += lc;
    }
    for (int i = 1; i <= maxp; ++i)
    {
        sumx[i] = sumx[i - 1] + dp[i];
    }
    long long maxl = -1;
    for (int j = 1; j <= maxp - w + 1; ++j)
    {
        long long cv = sumx[j + w - 1] - sumx[j - 1];
        // cout << cv << endl;
        maxl = max(maxl, cv);
    }
    cout << maxl << endl;
}