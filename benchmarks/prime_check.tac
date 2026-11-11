n = 29
d = 2
flag = 1
L:
r = n % d
if r goto N
flag = 0
goto E
N:
d = d + 1
c = d * d
t = c <= n
if t goto L
E:
print flag
