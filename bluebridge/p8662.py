def solve():
    n = 7
    imap = [".......", ".##....", ".##....", "....##.", "..####.", "...###.", "......."]
    vis = [[False] * n for _ in range(n)]
    q = []
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    ans = 0

    def bfs(x: int, y: int):
        global flag
        vis[x][y] = True
        q.append((x, y))
        while len(q):
            tx, ty = q.pop(0)
            if (
                imap[tx][ty + 1] == "#"
                and imap[tx + 1][ty] == "#"
                and imap[tx - 1][ty] == "#"
                and imap[tx][ty - 1] == "#"
            ):
                flag = False
            for dx, dy in directions:
                nx = tx + dx
                ny = ty + dy
                print(nx, ny)
                if not vis[nx][ny] and imap[nx][ny] == "#":
                    q.append((nx, ny))
                    vis[nx][ny] = 1

    for i in range(n):
        for j in range(n):
            if not vis[i][j] and imap[i][j] == "#":
                global flag
                flag = True
                bfs(i, j)
                if flag:
                    ans += 1

    print(ans)


solve()
