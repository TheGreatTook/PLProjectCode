#ifndef PYLIB_H
#define PYLIB_H

#include <iostream>
#include <stdexcept>
#include <string>
#include <cstring>
#include <sstream>

using namespace std;

class Variant {
 private:
  enum Type {
    UNKOWN = 0,
    INT,
    DOUBLE,
    BOOL,
    STRING
  };

  struct {
    Type type;
    union {
      int intVal;
      double realVal;
      bool boolVal;
      string* strVal;
    };
  } data;

 public:
  Variant();
  Variant(int v);
  Variant(double v);
  Variant(bool v);
  Variant(string v);

  Variant(const Variant& other);

  ~Variant();

  Variant& operator = (const Variant& other);
  Variant& operator = (int newVal);
  Variant& operator = (double newVal);
  Variant& operator = (bool newVal);
  Variant& operator = (string& newVal);

  operator int&();
  operator double&();
  operator bool&();
  operator string&();
};

double pMod(double left, double right);

#endif
