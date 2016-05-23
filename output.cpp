#include <iostream>
#include <math.h>
#include <string>
using namespace std;

template<typename T>
void doStuff(T const & z) {
  Variant var;
  var = 2;
  var = z;
  cout << (T&)var << endl;
}

template<typename T, typename U>
void addThenPrint(T const & x, U const & y) {
  T val;
  val = add(x,y);
  cout << x + y << endl;
}

template<typename T, typename U>
inline T const & add(T const & x, U const & y) {
  return x + y;
}

template<typename T>
void helloWorld(T const & string) {
  T introduction;
  introduction = string("Hello World! My name is ");
  T name;
  name = string;
  T greeting;
  greeting = introduction + name;
  cout << greeting << endl;
}

template<typename T, typename U, typename V>
void average(T const & n1, U const & n2, V const & n3) {
  T summ;
  T ave;
  if(n1 > 0  and n2 > 0  and n3 > 0 )
  {
    summ = n1 + n2 + n3;
    ave = summ / 3;
    cout << string("The average is ") << endl;
    cout << ave << endl;
  } 
  else
  { 
  cout << string("The average is 0") << endl;
  } 
}

template<typename >
void prime( {
  for(int n=2; n<13; n++) 
  {
    for(int x=2; x<n; x++) 
  {
    if(pMod(n,x) = 0 )
  {
    cout << n << string("equals") << x << string("*") << n / x << endl;
    } 
  else
  { 
  cout << n << string("is a prime number") << endl;
  } 
  } 
  } 
}

int main() {
  Variant b;
  b = 3;
  Variant a;
  a = 2.5;
  Variant c;
  c = add((double&)a,(int&)b);
  cout << (double&)c << endl;
  b = 4.5;
  a = 2;
  Variant d;
  d = add((int&)a,(double&)b);
  cout << (double&)d << endl;
  addThenPrint((double&)c,(double&)d);
  bool i;
  i = true;
  bool l;
  int j;
  if(i)
  {
    l = true;
    j = 5;
    b += 1;
  } 
  int k;
  for(int x=0; x<5; x++) 
  {
    k = 0;
    k += 2;
  } 
  while (a < 10 )
  {
  a += 1;
  } 
  if(a = 10 )
  {
    a = 5;
  } 
  else  if(a = "hi" )
  {
    a = "hello";
  } 
  cout << (int&)a << endl;
  doStuff((int&)a);
  doStuff((double&)b);
  helloWorld(string("Elinor"));
  average(4,6,8);
  return 0;
}