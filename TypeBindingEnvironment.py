class Function():
    def __init__(self, name):
        self.name = name
        self.arguments = []
        self.environment = TypeBindingEnvironment()
        self.returnType = 'void'
        self.template = False

    def addArgument(self, name):
        self.arguments.append(Variable(name))

class Variable():
    def __init__(self, name):
        self.name = name
        self.types = []
        self.boundType = 'void'
        self.ambiguous = False
    
    def addType(self, t):
        if not(t in self.types):
            self.types.append(t)

class TypeBindingEnvironment():
    def __init__(self):
        self.variables = []

    def size(self):
        return len(self.variables)

    def contains(self, name):
        for var in self.variables:
            if var.name == name:
                return True
        return False

    def find(self, name):
        for var in self.variables:
            if var.name == name:
                return var
        return None

    def add(self, var):
        self.variables.append(var)

    def dump(self, offset):
        prefix = ''
        for i in range(0, offset):
            prefix += '>>'

        print(prefix + '-----------------------------------')
        for var in self.variables:
            if isinstance(var, Variable):
                print(prefix + var.name, '{', var.types, var.boundType, var.ambiguous, '}')
            if isinstance(var, Function):
                print(prefix + var.name, '{')
                print(prefix + 'arguments:')
                for arg in var.arguments:
                    print(prefix + '>>' + arg.name, arg.types, arg.boundType, arg.ambiguous)
                print(prefix + 'environment:')
                var.environment.dump(offset + 1)
                print(prefix + var.returnType, var.template, '}')
        print(prefix + '-----------------------------------')
