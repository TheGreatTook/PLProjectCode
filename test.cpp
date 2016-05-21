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

class Variant {
private:
  enum Type {
    UNKOWN = 0,
    INT,
    DOUBLE,
    STRING
  };

  struct {
    Type type;
    union {
      int intVal;
      double realVal;
      string* strVal;
    };
  } data;

public:
  Variant() {
    data.type = UNKOWN;
    data.intVal = 0;
  }
  Variant(int v) {
    data.type = INT;
    data.intVal = v;
  }
  Variant(double v) {
    data.type = DOUBLE;
    data.realVal = v;
  }
  Variant(string v) {
    data.type = STRING;
    data.strVal = new string(v);
  }

  Variant(const Variant& other) {
    *this = other;
  }

  ~Variant() {
    if(data.type == STRING) {
      delete data.strVal;
    }
  }

  Variant& operator = (const Variant& other) {
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
  Variant& operator = (int newVal) {
    if(data.type == STRING) {
      delete data.strVal;
    }

    data.type = INT;
    data.intVal = newVal;

    return *this;
  }
  Variant& operator = (double newVal) {
    if(data.type == STRING) {
      delete data.strVal;
    }

    data.type = DOUBLE;
    data.realVal = newVal;

    return *this;
  }
  Variant& operator = (string& newVal) {
    if(data.type == STRING) {
      delete data.strVal;
    }

    data.type = STRING;
    data.strVal = new string(newVal);

    return *this;
  }

  operator int&() {
    if(data.type == INT) {
      return data.intVal;
    }

    throw runtime_error("bad cast");
  }

  operator double&() {
    if(data.type == DOUBLE) {
      return data.realVal;
    }

    throw runtime_error("bad cast");
  }

  operator string&() {
    if(data.type == STRING) {
      return *data.strVal;
    }

    throw runtime_error("bad cast");
  }
};

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

template <typename T>
inline T const & dynamicType(T const & num) {
  return num;
}

template <typename T, typename U> 
inline T const & add(T const & a, U const & b) {
  return a + b;
}

int main() {
  Variant v = string("test");
  v = 1;
  v = 2.5;
  v = string("testing");
  Variant v2;
  v2 = v;
  cout << (string&)v2 << endl;

  cout << endl;

  cout << add(4.5, 4) << endl;

  cout << pMod(5.5, 4) << endl;

  return 0;
}
