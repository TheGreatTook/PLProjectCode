#include <iostream>
#include <math.h>
#include <string>
using namespace std;

template <typename T>
Variant add(int a, T const & b) {
  string f;
  f = string("look a local variable");
  T z;
  z = b;
  T x_xx;
  x_xx = z + string("noooo!");
  return a + b;
}

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  double c;
  c = (double&)a + (double&)b;
  string d;
  d = string("test");
  cout << d << endl;
  int e;
  e = b = 3;
  cout << (int&)b << endl;
  add(e,(int&)b);
  add(1,5.5);
  Variant z;
  z = add(1,5.5);
  cout << (double&)z << string("cool") << endl;
  a = string("hello world").append(string("!"));
  cout << (string&)a << endl;
  double f;
  f = c + e;
  Variant x;
  x = pow(5,2);
  cout << (int&)x << endl;
  x = string("5**2");
  string y;
  y = (string&)x;
  cout << (string&)x << endl;
  return 0;
}