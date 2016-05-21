#include <iostream>
#include <string>
using namespace std;

template <typename T>
inline T const & add(int a, T const & b) {
  string f = string("look a local variable");
  return a + b;
}

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  float c = (float&)a + (float&)b;
  string d = string("test");
  cout << d << endl;
  int e;
  e = b = 3;
  cout << (int&)b << endl;
  add(e, (int&)b);
  a = string("hello world");
  cout << (string&)a << endl;
  float f = c + e;
  return 0;
}