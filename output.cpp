#include <iostream>
#include <string>
using namespace std;

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  float c = (float&)a + (float&)b;
  string d = string("test");
  int e;
  b = e = 3;
  a = string("hello world");
  float f = c + e;
  return 0;
}