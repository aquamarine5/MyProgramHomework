n, m = [int(x) for x in input().split()]
pic = [input() for _ in range(n)]
directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
from collections import deque


def bfs(start_x: int, start_y: int):
    walked = [[False] * n for _ in range(n)]
    queue = deque([(start_x, start_y)])

    count = 1

    while queue:
        x, y = queue.popleft()
        is0 = pic[x][y] == "0"
        walked[x][y] = True
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n and not walked[nx][ny]:  # 边界检查改为n
                # 如果当前是0，则只能走到1；如果当前是1，则只能走到0
                if (is0 and pic[nx][ny] == "1") or (not is0 and pic[nx][ny] == "0"):
                    walked[nx][ny] = True
                    queue.append((nx, ny))
                    count += 1

    return count


for _ in range(m):
    x, y = [int(x) for x in input().split()]
    x -= 1  # 转换为0索引
    y -= 1
    print(bfs(x, y))
