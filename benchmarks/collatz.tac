n = 19
s = 0
L:
r = n % 2
if r goto O
n = n / 2
goto C
O:
n = n * 3
n = n + 1
C:
s = s + 1
t = s < 20
if t goto L
print s
