#include "pylib.h"

#include <iostream>
#include <stdexcept>
#include <string>
#include <cstring>
#include <sstream>

using namespace std;

namespace patch {
  template <typename T> std::string to_string(const T& n) {
    std::ostringstream stm;
    stm << n;
    return stm.str();
  }

  int stoi(string str) {
    std::stringstream stm(str);
    int n;
    stm << str;
    stm >> n;
    return n;
  }
}

Variant::Variant() {
  data.type = UNKOWN;
  data.intVal = 0;
}
Variant::Variant(int v) {
  data.type = INT;
  data.intVal = v;
}
Variant::Variant(double v) {
  data.type = DOUBLE;
  data.realVal = v;
}
Variant::Variant(bool v) {
  data.type = BOOL;
  data.boolVal = v;
}
Variant::Variant(string v) {
  data.type = STRING;
  data.strVal = new string(v);
}

Variant::Variant(const Variant& other) {
  *this = other;
}

Variant::~Variant() {
  if(data.type == STRING) {
    delete data.strVal;
  }
}

Variant& Variant::operator = (const Variant& other) {
  if(this != &other) {
    if(data.type == STRING) {
      delete data.strVal;
    }
      
    switch(other.data.type) {
    case STRING: {
      data.strVal = new string(*(other.data.strVal));
      data.type = STRING;
      break;
    }
    default: {
      memcpy(this, &other, sizeof(Variant));
      break;
    }
    }
  }
  
  return *this;
}
Variant& Variant::operator = (int newVal) {
  if(data.type == STRING) {
    delete data.strVal;
  }

  data.type = INT;
  data.intVal = newVal;

  return *this;
}
Variant& Variant::operator = (double newVal) {
  if(data.type == STRING) {
    delete data.strVal;
  }

  data.type = DOUBLE;
  data.realVal = newVal;

  return *this;
}
Variant& Variant::operator = (bool newVal) {
  if(data.type == STRING) {
    delete data.strVal;
  }

  data.type = BOOL;
  data.boolVal = newVal;

  return *this;
}
Variant& Variant::operator = (string& newVal) {
  if(data.type == STRING) {
    delete data.strVal;
  }

  data.type = STRING;
  data.strVal = new string(newVal);

  return *this;
}

Variant::operator int&() {
  if(data.type == INT) {
    return data.intVal;
  }

  throw runtime_error("bad cast");
}

Variant::operator double&() {
  if(data.type == DOUBLE) {
    return data.realVal;
  }

  throw runtime_error("bad cast");
}

Variant::operator bool&() {
  if(data.type == BOOL) {
    return data.boolVal;
  }

  throw runtime_error("bad cast");
}

Variant::operator string&() {
  if(data.type == STRING) {
    return *data.strVal;
  }

  throw runtime_error("bad cast");
}

double pMod(double left, double right) {
  double val = left / right;
  string sVal = patch::to_string(val);

  for(int i = 0; i < sVal.length(); i++) {
    if(sVal[i] == '.') {
      sVal = sVal.substr(0, i);
      break;
    }
  }

  return (val - patch::stoi(sVal)) * right;
}
