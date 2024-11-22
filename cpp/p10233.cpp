#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int T;
    cin >> T;
    while (T--)
    {
        string s;
        cin >> s;
        vector<int> v(s.size()), sum(s.size() + 1);
        sum[0] = 0;
        for (int i = 0; i < s.size(); i++)
        {
            char c = s[i];
            int k = 0;
            if (c == 'P')
                k = 3;
            else if (c == 'p')
                k = 2;
            else if (c == 'G')
                k = 1;
            sum[i + 1] = sum[i] + k;
        }
        int q;
        cin >> q;
        while (q--)
        {
            int s, e;
            cin >> s >> e;
            cout << (sum[e] - sum[s - 1]) << endl;
        }
    }
}