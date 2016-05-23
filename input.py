def doStuff(z):
    var = 2
    var = z
    print(var)

def addThenPrint(x,y):
    val = add(x,y)
    print(val)

def add(x,y):
    return x + y

b=3
a=2.5
c = b + a
c=add(a,b)
print(c)
b=4.5
a=2
d=add(a,b)
print(d)
addThenPrint(c,d)
doStuff(a)
doStuff(b)
