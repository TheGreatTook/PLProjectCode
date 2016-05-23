def printNumbers():
	a = 0
	while a < 50:
		print(a)

def studentLoans(loan, interest, months):
	principal = loan
	rate = interest/12
	timePeriod = months
	numerator = rate*(1+rate)**timePeriod
	denominator = (1+rate)**timePeriod - 1
	payment = principal*(numerator/denominator)
	print("You will pay:", payment, "dollars per month")

def prime():
        for n in range(2, 13):
                for x in range(2, n):
                        if n % x == 0:
                                print(n, "equals", x, "*", n/x)
                                break
                        else:
                                print(n, "is a prime number")


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

print("Print some Numbers")
printNumbers()
print("\n")

print("Student Loan Calculator Function")
studentLoans(30000, 0.03, 120)
print("\n")

print("Prime numbers function")
prime()
print("\n")

print("Hello world function")
helloWorld("Elinor")
print("\n")

print("Average function")
average(12, 30, 6)
