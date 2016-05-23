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
  return 0;
}