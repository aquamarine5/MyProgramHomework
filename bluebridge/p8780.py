a, b, n = [int(x) for x in input().split()]
days = 0
t = 0
weeks = 5 * a + 2 * b
days += n // weeks * 7
p = n % weeks
pd = 0
while t < p:
    pd += 1
    if pd <= 5:
        t += a
    else:
        t += b
print(days + pd)
