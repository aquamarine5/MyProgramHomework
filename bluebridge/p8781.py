n = int(input())
for i in range(1, n + 1):
    print(max(n - i, i - 1) * 2)
