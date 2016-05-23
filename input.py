def doStuff(z):
    var = 2
    var = z
    print(var)

def addThenPrint(x,y):
    val = add(x,y)
    #val = x + y
    print(x + y)

def add(x,y):
    return x + y

def helloWorld(string):
        introduction = "Hello World! My name is "
        name = string
        greeting = introduction + name
        print(greeting)             

def average(n1, n2, n3):
        if n1 > 0 and n2 > 0 and n3 >0:
                summ = n1 + n2 + n3
                ave = summ/3
                print("The average is ")
                print(ave)
        else:
                print("The average is 0")

b=3
a=2.5
c=add(a,b)
print(c)
b=4.5
a=2
d=add(a,b)
print(d)
addThenPrint(c,d)

i=True
if i:
	l=True
	j=5
	b+=1

for x in range (0, 5):
	k=0
	k+=2
while (a < 10):
	a += 1

if a == 10:
	a=5
elif a == 'hi':
	a = 'hello'
print(a)
doStuff(a)
doStuff(b)

helloWorld("Elinor")

average(4, 6, 8)