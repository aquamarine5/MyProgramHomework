/*
 * @Author: aquamarine5 && aquamarine5_@outlook.com
 * Copyright (c) 2024 by @aquamarine5, RC. All Rights Reversed.
 */
#include <iostream>
#include <vector>
using namespace std;
int main()
{
    int l;
    cin >> l;
    while (l--)
    {
        string a, b;
        cin >> a >> b;
        cout << b[0] << a[1] << a[2] << " " << a[0] << b[1] << b[2] << endl;
    }
}