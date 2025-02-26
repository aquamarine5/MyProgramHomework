n = int(input())
from collections import deque

queue = deque([(1, 0)])
visited = set([1])
while queue:
    pos, steps = queue.popleft()
    if pos == n:
        print(steps)
        break
    for next_pos in [pos - 1, pos + 1, pos * 2]:
        if 1 <= next_pos <= n and next_pos not in visited:
            visited.add(next_pos)
            queue.append((next_pos, steps + 1))
