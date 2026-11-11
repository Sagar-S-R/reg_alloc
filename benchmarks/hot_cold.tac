y = 100
x = 0
i = 0
L1:
x = x + 1
x = x * 2
x = x % 1000003
i = i + 1
c = i < 1000
if c goto L1
print y
print x
