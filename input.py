def add(a,b):
    f="look a local variable"
    return a + b

a=b=1+1.5*2
c=a+b
d="test"
print(d)
e=b=3
print(b)
add(e,b)
a="hello world"
print(a)
f=c+e
