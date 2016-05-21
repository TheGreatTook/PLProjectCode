#include <iostream>
#include <string>
using namespace std;

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  float c = (float&)a + (float&)b;
  string d = string("test");
  cout << d << endl;
  int e;
  e = b = 3;
  cout << (int&)b << endl;
  a = string("hello world");
  cout << (string&)a << endl;
  float f = c + e;
  return 0;
}