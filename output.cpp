#include <iostream>
#include <string>
#include <math.h>
using namespace std;

int main() {
  Variant a, b;
  a = b = 1 + 1.5 * 2;
  float c = (float&)a + (float&)b;
  string d = string("test");
  int e;
  b = e = 3;
  a = string("hello world");
  bool g = True;
  bool h = (int&)b < c ;
  bool i = True;
  float k = pow(e,(int&)b);
  bool j = g (string&)and i;
  if(g and i)
  {
  return j;
  } 
  else 
  { 
  return i;
  } 
  float f = c + e;
  while (i)
  {
  return j;
  } 
  return 0;
}