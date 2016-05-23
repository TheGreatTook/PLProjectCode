#include "pylib.h"
#include <iostream>
#include <math.h>
#include <string>
using namespace std;

template<typename T>
void doStuff(T const & z);

template<typename T, typename U>
void addThenPrint(T const & x, U const & y);

template<typename T, typename U>
inline T const & add(T const & x, U const & y);

template<typename T>
void helloWorld(T const & s);

template<typename T, typename U, typename V>
void average(T const & n1, U const & n2, V const & n3);

template<typename T>
void prime(T const & num);

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
  cout << val << endl;
}

template<typename T, typename U>
inline T const & add(T const & x, U const & y) {
  return x + y;
}

template<typename T>
void helloWorld(T const & s) {
  string introduction;
  introduction = string("Hello World! My name is ");
  T name;
  name = s;
  T greeting;
  greeting = introduction + name;
  cout << greeting << endl;
}

template<typename T, typename U, typename V>
void average(T const & n1, U const & n2, V const & n3) {
  T summ;
  T ave;
  if(n1 > 0 and n2 > 0 and n3 > 0)
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

template<typename T>
void prime(T const & num) {
  for(int n=2; n<num; n++) 
  {
    for(int x=2; x<n; x++) 
  {
    if(pMod(n,x) == 0)
  {
    cout << n << string("equals") << x << string("*") << n / x << endl;
    break;
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
  c = (int&)b + (double&)a;
  c = add((double&)a,(int&)b);
  cout << (double&)c << endl;
  b = 4.5;
  a = 2;
  Variant d;
  d = add((int&)a,(double&)b);
  cout << (int&)d << endl;
  addThenPrint((double&)c,(int&)d);
  bool i;
  i = true;
  bool l;
  int j;
  if(i)
  {
    l = true;
    j = 5;
    b = (double&)b+1;
  } 
  int k;
  for(int x=0; x<5; x++) 
  {
    k = 0;
    k = k+2;
  } 
  while ((int&)a < 10)
  {
  a = (int&)a+1;
  } 
  cout << (int&)a << endl;
  doStuff((int&)a);
  doStuff((double&)b);
  string name;
  name = string("Elinor");
  helloWorld(name);
  average(4,6,8);
  prime(13);
  return 0;
}