f = open('airboat.obj', 'r')
lines = f.readlines()
ls = []
for l in lines:
    if l[0] == 'v':
        e = l.split()
        ls.append((float(e[1]), float(e[2]), float(e[3])))
print(ls)
