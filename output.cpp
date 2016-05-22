#include <iostream>
#include <math.h>
#include <string>
using namespace std;

template <typename T, typename U>
void addThenPrint(T const & x, U const & y) {
  T val;
  val = x + y;
  cout << x + y << endl;
}

template <typename T, typename U>
Variant add(T const & x, U const & y) {
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
  return 0;
}