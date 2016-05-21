#include <iostream>
#include <string>
#include <math.h>
using namespace std;

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  float c = (float&)a + (float&)b;
  string d = string("test");
  cout << d << endl;
  int e;
  e = b = 3;
<<<<<<< HEAD
  cout << (int&)b << endl;
=======
>>>>>>> 1bcbd0d2f2a6b31cb9472f839788773c2475c9fa
  a = string("hello world");
  cout << (string&)a << endl;
  float f = c + e;
  return 0;
}