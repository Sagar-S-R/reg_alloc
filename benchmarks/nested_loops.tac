sum = 0
a = 3
b = 4
i = 0
L1:
j = 0
L2:
k = 0
L3:
x = i + j
x = x + k
sum = sum + x
k = k + 1
c = k < 3
if c goto L3
j = j + 1
d = j < 3
if d goto L2
i = i + 1
e = i < 3
if e goto L1
print sum
print a
print b
