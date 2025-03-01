n, k = [int(x) for x in input().split()]
mp = [" " * (n + 1)] + [" " + input() for _ in range(n)]
vis = [[[False] * 3 for _ in range(n + 1)] for _ in range(n + 1)]
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
from collections import deque


def check(x: int, y: int, size: int):
    left = max(1, x - size)
    right = min(n, x + size)
    top = max(1, y - size)
    bottom = min(n, y + size)
    if left > x - size or right < x + size or top > y - size or bottom < y + size:
        return False
    for i in range(x - size, x + size + 1):
        for j in range(y - size, y + size + 1):
            # print(i, j)
            if mp[i][j] == "*":
                return False
    return True


def bfs(x: int, y: int):
    ql = deque([(x, y, 0)])
    ex, ey = n - 2, n - 2

    vis[x][y][2] = True
    while ql:
        tx, ty, step = ql.popleft()
        size = 2 if step < k else 1 if step < 2 * k else 0
        if tx == ex and ty == ey:
            print(step)
            return
        for dx, dy in directions:
            if tx + dx == ex and ty + dy == ey:
                print(step + 1)
                return
            if check(tx + dx, ty + dy, size) and not vis[tx + dx][ty + dy][size]:
                vis[tx + dx][ty + dy][size] = True
                ql.append((tx + dx, ty + dy, step + 1))
        if size > 0:
            ql.append((tx, ty, step + 1))


bfs(3, 3)
