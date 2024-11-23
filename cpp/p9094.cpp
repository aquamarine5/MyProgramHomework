#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int n, m;
    cin >> n >> m;
    vector<int> bluex(n + 10, 0), yellowx(n + 10, 0), redx(n + 10, 0);
    while (m--)
    {
        int s, e, c;
        cin >> s >> e >> c;
        if (c == 2)
        {
            bluex[s]++;
            bluex[e + 1]--;
        }
        else if (c == 1)
        {
            yellowx[s]++;
            yellowx[e + 1]--;
        }
        else
        {
            redx[s]++;
            redx[e + 1]--;
        }
    }
    int r = 0;
    for (int i = 1; i <= n; i++)
    {
        bluex[i] += bluex[i - 1];
        yellowx[i] += yellowx[i - 1];
        redx[i] += redx[i - 1];
    }
    for (int i = 1; i <= n; i++)
    {
        if (yellowx[i] && bluex[i] && redx[i] == 0)
        {
            r++;
        }
    }
    cout << r << endl;
}