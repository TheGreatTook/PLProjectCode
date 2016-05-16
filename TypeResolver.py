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

#The TypeResolver class is responsible for resolving the list of possible types
#each variable in the python source can be bound to. TypeResolve achieves this by doing
#an initial pass over the python source AST. Additionally TypeResolver can
#be used to resolve the type of a python expressions at translation time.
class TypeResolver(ast.NodeVisitor):
    #Class Constructor
    def __init__(self):
        self.expressionType = 'null'
        self.variables = VariableCollection()
        self.boundVariables = VariableTypeEnvironment()

    #Initiates the initial pass over the AST.
    #Arguments:
    #   tree: The python source AST.
    def initialize(self, tree):
        self.visit(tree)

    #Dumps the list of variables and their corresponding 
    #binding types to standard output.
    def dump(self):
        self.variables.dump()

    #Resolves the type of a given variable. Note variables with 
    #multiple binding will be considered variants while variables
    #with only a single binding type will be considered that type.
    #Arguments:
    #   name: The variable name.
    #Returns:
    #   The variable type.
    def resolveVariableType(self, name):
        var = self.variables.find(name)
        if len(var.types) > 1:
            return 'Variant'
        elif len(var.types) == 1:
            return var.types[0]
        else:
            return 'unknow'

    #Resolves the type of a given python expression.
    #Arguments:
    #   expr: The python expression.
    #Returns:
    #   The python expression type.
    def resolveExpressionType(self, expr):
        if 'string(' in expr:
            self.expressionType = 'string'
        else:
            self.visit(ast.parse(expr))
        return self.expressionType
    
    #Flagged for refactor.
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
    
    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    #Visits a Num AST node and resolves it's primitive type.
    #Arguments:
    #   node: The AST node.
    #Returns:
    #   The primitive type(float or int) of the value.
    def visit_Num(self, node):
        value = str(node.n)
        for c in value:
            if c == '.':
                return 'float'
        return 'int'

    #Visits a Str AST node and resolves it's primitive type.
    #Arguments:
    #   node: The AST node.
    #Returns:
    #   The primitive type(string) of the value.
    def visit_Str(self, node):
        return 'string'

    #-----------------------
    #-----Variable Node-----
    #-----------------------
    #Visits a Name AST node and adds the variable name to the collection of variables.
    #Arguments:
    #   node: The AST node.
    #Returns:
    #   The Variable name.
    def visit_Name(self, node):
        if not(self.variables.contains(node.id)):
            self.variables.add(node.id)
        return node.id

    #--------------------------
    #-----Expression Nodes-----
    #--------------------------
    #Visits an Expr AST Node and stores its expression type.
    #Arguments:
    #   node: The AST node.
    def visit_Expr(self, node):
        self.expressionType = self.visit(node.value)

    #Visits a BinOp AST Node and resolves it's primitive type.
    #Arguments:
    #   node: The AST node.
    #Returns:
    #   The primitive type(string, float or int) of the binary operation.
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

    #Visits a BoolOp AST Node and resolves it's primitive type.
    #Arguments:
    #   node: The AST node.
    #Returns:
    #   The primitive type(bool) of the bool operation.
    def visit_BoolOp(self, node):
        return 'bool'

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    #Visits an Assign AST node and adds the primitive type of the value
    #to each target variables collection of binding types.
    #Arguments:
    #   node: The AST node.
    def visit_Assign(self, node):
        names = []
        for target in node.targets:
            names.append(self.visit(target))

        varType = self.visit(node.value)

        for name in names:
            self.variables.extend(name, varType)
