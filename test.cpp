#include <iostream>
#include <stdexcept>
#include <string>
#include <cstring>

using namespace std;

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

template <typename T>
inline void print(T const & val) {
  cout << val << endl;
}

template <typename T>
inline T const & dynamicType(T const & num) {
  return num;
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

  int intVal = 5;
  print(intVal);
  float floatVal = 5.5;
  print(floatVal);

  cout << endl;

  cout << dynamicType(0) << endl;

  return 0;
}
