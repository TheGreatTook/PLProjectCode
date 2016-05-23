#This is a demo Python program that uses as many implemented features as possible

#Prints all of the Fibonacci numbers that are less than b
def fibonacci():
	a, b = 0, 1
	while b < 200:
		print(b)
		a, b = b, a+b

#Prints the amount of money a graduate will pay per month
#loan is the principal loan amount
#interest is the annual interest rate, and we're assuming that you make a payment every month
#months is the number of months you're paying for
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

#A basic, cute hello world program
def helloWorld(string):
        introduction = "Hello World! My name is "
        name = string
        greeting = introduction + name
        print(greeting)

#Average function
def average(n1, n2, n3):
        if not(n1 == n2 == n3 == 0):
                average = (n1 + n2 + n3)/3
                print("The average is", average)
        else:
                print("The average is 0")

print("Fibonacci Function")
fibonacci()
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
