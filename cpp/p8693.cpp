#include <iostream>
#include <vector>
#include <queue>
#include <tuple>
#include <string>
using namespace std;

int n, k;
vector<string> mp;
vector<vector<vector<bool>>> vis;
// 四个方向：右、左、下、上
int dx[] = {0, 0, 1, -1};
int dy[] = {1, -1, 0, 0};

// 检查在给定位置和大小下是否合法
bool check(int x, int y, int size)
{
    int left = max(1, x - size);
    int right = min(n, x + size);
    int top = max(1, y - size);
    int bottom = min(n, y + size);

    // 检查边界条件
    if (left > x - size || right < x + size || top > y - size || bottom < y + size)
        return false;

    // 检查区域内是否有障碍物
    for (int i = x - size; i <= x + size; i++)
    {
        for (int j = y - size; j <= y + size; j++)
        {
            if (mp[i][j] == '*')
                return false;
        }
    }
    return true;
}

void bfs(int x, int y)
{
    queue<tuple<int, int, int>> q; // 存储 x, y, step
    int ex = n - 2, ey = n - 2;    // 终点坐标

    q.push(make_tuple(x, y, 0));
    vis[x][y][2] = true; // 初始是大胖子状态(size=2)

    while (!q.empty())
    {
        auto [tx, ty, step] = q.front();
        q.pop();

        // 计算当前体型大小
        int size = (step < k) ? 2 : (step < 2 * k) ? 1
                                                   : 0;

        // 检查是否到达终点
        if (tx == ex && ty == ey)
        {
            cout << step << endl;
            return;
        }

        // 尝试四个方向移动
        for (int i = 0; i < 4; i++)
        {
            int nx = tx + dx[i];
            int ny = ty + dy[i];

            // 提前检查是否到达终点
            if (nx == ex && ny == ey)
            {
                cout << step + 1 << endl;
                return;
            }

            // 检查移动是否合法且未访问过
            if (check(nx, ny, size) && !vis[nx][ny][size])
            {
                vis[nx][ny][size] = true;
                q.push(make_tuple(nx, ny, step + 1));
            }
        }

        // 如果当前非正常人，可以原地等待变瘦
        if (size > 0)
        {
            q.push(make_tuple(tx, ty, step + 1));
        }
    }
}

int main()
{
    cin >> n >> k;

    // 初始化地图，增加一行一列作为边界
    mp.resize(n + 1);
    mp[0] = string(n + 1, ' ');
    for (int i = 1; i <= n; i++)
    {
        mp[i] = " ";
        string row;
        cin >> row;
        mp[i] += row;
    }

    // 初始化访问数组
    vis.resize(n + 1, vector<vector<bool>>(n + 1, vector<bool>(3, false)));

    // 从起点开始BFS
    bfs(3, 3);

    return 0;
}