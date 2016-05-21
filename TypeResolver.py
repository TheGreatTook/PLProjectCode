import ast

class Variable():
    def __init__(self, name):
        self.name = name
        self.types = []
        self.boundType = 'void'
        self.ambiguous = False
    
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
            print(var.name, var.types, var.boundType, var.ambiguous)
        print('---------------')

#The TypeResolver class is responsible for resolving the list of possible types
#each variable in the python source can be bound to. TypeResolve achieves this by doing
#an initial pass over the python source AST. Additionally TypeResolver can
#be used to resolve the type of a python expressions at translation time.
class TypeResolver(ast.NodeVisitor):
    #Class Constructor
    def __init__(self):
        self.variableCollection = VariableCollection()
        self.variables = self.variableCollection.variables

    #Initiates the initial pass over the AST.
    #Arguments:
    #   tree: The python source AST.
    def initialize(self, tree):
        self.visit(tree)

    #Dumps the list of variables and their corresponding 
    #binding types to standard output.
    def dump(self):
        self.variableCollection.dump()

    #Resolves the type of a given variable. Note variables with 
    #multiple binding will be considered variants while variables
    #with only a single binding type will be considered that type.
    #Arguments:
    #   name: The variable name.
    #Returns:
    #   The variable type.
    def resolveVariableType(self, name):
        var = self.variableCollection.find(name)
        if len(var.types) > 1:
            return 'Variant'
        elif len(var.types) == 1:
            return var.types[0]
        else:
            return 'void'

    #Resolves the type of a given python expression.
    #Arguments:
    #   expr: The python expression.
    #Returns:
    #   The python expression type.
    def resolveExpressionType(self, node):
        return self.visit(node)
    
    #Updates the primitive type bound to variables.
    #Arguments:
    #   variables: The variables to update.
    #   primitiveType: The primitiveType to bind.
    def updateBoundTypes(self, variables, primitiveType):
        for variable in variables:
            self.variableCollection.find(variable).boundType = primitiveType

    #Returns the type bound to the given variable.
    #Arguments:
    #   variable: The variable.
    def boundType(self, variable):
        return self.variableCollection.find(variable).boundType
    
    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    def visit_Num(self, node):
        value = str(node.n)
        for c in value:
            if c == '.':
                return 'float'
        return 'int'

    def visit_Str(self, node):
        return 'string'

    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        if not(self.variableCollection.contains(node.id)):
            self.variableCollection.add(node.id)
        return node.id

    #------------------------
    #----Expression Nodes----
    #------------------------
    def visit_BinOp(self, node):
        leftType = self.visit(node.left)
        rightType = self.visit(node.right)

        if self.variableCollection.contains(leftType):
            leftType = self.resolveVariableType(leftType)
        if self.variableCollection.contains(rightType):
            rightType = self.resolveVariableType(rightType)
        
        if leftType == 'string' or rightType == 'string':
            return 'string'
        elif leftType == 'float' or rightType == 'float':
            return 'float'
        else:
            return 'int'

    def visit_BoolOp(self, node):
        return 'bool'

    def visit_IfExp(self, node):
        print("TEST")

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        names = []
        for target in node.targets:
            names.append(self.visit(target))

        primitiveType = self.visit(node.value)

        for name in names:
            self.variableCollection.extend(name, primitiveType)
