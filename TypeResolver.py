import ast

class VariableTypeEnvironment():
    def __init__(self):
        self.variables = []
        self.types = []

    def contains(self, var):
        if var in self.variables:
            return True
        return False

    def extend(self, var, t):
        if not(var in self.variables):
            self.variables.append(var)
            self.types.append(t)

    def update(self, var, t):
        for i in range(0, len(self.variables)):
            if self.variables[i] == var:
                self.types[i] = t

    def apply(self, var):
        for i in range(0, len(self.variables)):
            if self.variables[i] == var:
                return self.types[i]

class Variable():
    def __init__(self, name):
        self.name = name
        self.types = []
    
    def addType(self, t):
        if not(t in self.types):
            self.types.append(t)

class VariableCollection():
    def __init__(self):
        self.variables = []

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

    def add(self, name):
        self.variables.append(Variable(name))

    def extend(self, name, t):
        self.find(name).addType(t)

    def dump(self):
        print('---------------')
        for var in self.variables:
            print(var.name, var.types)
        print('---------------')

class TypeResolver(ast.NodeVisitor):
    def __init__(self):
        self.expressionType = 'null'
        self.variables = VariableCollection()
        self.boundVariables = VariableTypeEnvironment()

    def initialize(self, tree):
        self.visit(tree)

    def dump(self):
        self.variables.dump()

    def resolveVariableType(self, name):
        var = self.variables.find(name)
        if len(var.types) > 1:
            return 'Variant'
        elif len(var.types) == 1:
            return var.types[0]
        else:
            return 'unknow'

    def resolveExpressionType(self, expr):
        if 'string(' in expr:
            self.expressionType = 'string'
        else:
            self.visit(ast.parse(expr))
        return self.expressionType
    
    def updateBoundVars(self, variants, primitives, primitiveType):
        for variant in variants:
            if not(self.boundVariables.contains(variant[0])):
                self.boundVariables.extend(variant[0], primitiveType)
            else:
                self.boundVariables.update(variant[0], primitiveType)

        for primitive in primitives:
            if not(self.boundVariables.contains(primitive[0])):
                self.boundVariables.extend(primitive[0], primitiveType)
            else:
                self.boundVariables.update(primitive[0], primitiveType)
    
    #Literal Nodes
    def visit_Num(self, node):
        value = str(node.n)
        for c in value:
            if c == '.':
                return 'float'
        return 'int'

    def visit_Str(self, node):
        return 'string'

    #Variable Node
    def visit_Name(self, node):
        if not(self.variables.contains(node.id)):
            self.variables.add(node.id)
        return node.id

    #Expression Nodes
    def visit_Expr(self, node):
        self.expressionType = self.visit(node.value)

    def visit_BinOp(self, node):
        leftType = self.visit(node.left)
        rightType = self.visit(node.right)

        if self.variables.contains(leftType):
            leftType = self.boundVariables.apply(leftType)
        if self.variables.contains(rightType):
            rightType = self.boundVariables.apply(rightType)
        
        if leftType == 'string' or rightType == 'string':
            return 'string'
        elif leftType == 'float' or rightType == 'float':
            return 'float'
        else:
            return 'int'

    def visit_BoolOp(self, node):
        return 'bool'

    #Statement Nodes
    def visit_Assign(self, node):
        names = []
        for target in node.targets:
            names.append(self.visit(target))

        varType = self.visit(node.value)

        for name in names:
            self.variables.extend(name, varType)
