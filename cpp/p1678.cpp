#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int m, n;
    cin >> m >> n;
    vector<int> pis(m), sss(n);
    for (int i = 0; i < m; ++i)
    {
        cin >> pis[i];
    }
    for (int i = 0; i < n; ++i)
    {
        cin >> sss[i];
    }
    long long ans = 0;
    sort(pis.begin(), pis.end());
    for (int i = 0; i < n; ++i)
    {
        int lp = lower_bound(pis.begin(), pis.end(), sss[i]) - pis.begin();
        if (lp == 0)
        {
            ans += pis[lp] - sss[i];
            // cout << pis[lp] << " " << pis[lp - 1] << " " << sss[i] << " " << ans << endl;
            continue;
        }
        if (lp == m)
        {
            ans += sss[i] - pis[lp - 1];
            continue;
        }
        ans += min(pis[lp] - sss[i], sss[i] - pis[lp - 1]);
        // cout << pis[lp] << " " << pis[lp - 1] << " " << sss[i] << " " << ans << endl;
    }
    cout << ans << endl;
}