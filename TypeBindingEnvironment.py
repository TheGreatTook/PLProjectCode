#The Function class is a data structure representing a function
#in the python source. It contains the name of a function along with
#all the typing information associated with that function.
#Function's are stored in the type binding environment.
class Function():
    def __init__(self, name):
        self.name = name
        self.arguments = []
        self.environment = TypeBindingEnvironment()
        self.body = None
        self.returnType = 'void'
        self.boundType = 'void'

    def addArgument(self, name):
        self.arguments.append(Variable(name))

    def extendArguments(self, argTypes):
        for i in range(0, len(argTypes)):
            self.arguments[i].addType(argTypes[i])

#The Variable class is a data structure representing a variable
#in the python source. It contains the name of a variable along with
#all the typing information associated with that variable.
#Variable's are stored in the type binding environment.
class Variable():
    def __init__(self, name):
        self.name = name
        self.types = []
        self.boundType = 'void'
    
    def addType(self, t):
        if not(t in self.types):
            self.types.append(t)

#The TypeBindingEnvironment class is a data structure that holds
#all the relevant typing information for every variable and function
#found in the python source. The TypeBindingEnvironment is used by
#the type resolver at translation time to retrieve the appropriate typing 
#information associated with variables and functions.
class TypeBindingEnvironment():
    def __init__(self):
        self.elements = []

    def size(self):
        return len(self.elements)

    def contains(self, name):
        for elt in self.elements:
            if elt.name == name:
                return True
        return False

    def find(self, name):
        for elt in self.elements:
            if elt.name == name:
                return elt
        return None

    def add(self, elt):
        self.elements.append(elt)

    def clearBindings(self):
        for elt in self.elements:
            elt.boundType = 'void'
            if isinstance(elt, Function):
                elt.environment.clearBindings()
                for arg in elt.arguments:
                    arg.boundType = arg.types[0]

    def dump(self, offset):
        prefix = ''
        for i in range(0, offset):
            prefix += '>>'

        print(prefix + '-----------------------------------')
        for elt in self.elements:
            if isinstance(elt, Variable):
                print(prefix + elt.name, '{', elt.types, elt.boundType, '}')
            if isinstance(elt, Function):
                print(prefix + elt.name, '{')
                print(prefix + 'arguments:')
                for arg in elt.arguments:
                    print(prefix + '>>' + arg.name, arg.types, arg.boundType)
                print(prefix + 'environment:')
                elt.environment.dump(offset + 1)
                print(prefix + 'returns:')
                print(prefix + '>>' + elt.returnType)
                print(elt.boundType, '}')
        print(prefix + '-----------------------------------')
