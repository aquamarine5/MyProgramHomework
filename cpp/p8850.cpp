#include <iostream>
#include <vector>
#include <algorithm>
using namespace std;
int main()
{
    int T;
    cin >> T;
    while (T--)
    {
        int n, x;
        cin >> n >> x;
        vector<int> a(10);
        bool flag = false;
        for (int i = 1; i <= n; i++)
        {
            cin >> a[i];
            if ((a[i] > 0 && x > 0) || (a[i] < 0 && x < 0))
            {
                flag = true;
            }
            if (a[i] != a[i - 1] && i != 1)
                flag = true;
            if (abs(x) % abs(a[i]))
                flag = true;
        }
        if (flag)
            cout << "Yes" << endl;
        else
            cout << "No" << endl;
    }
    return 0;
}