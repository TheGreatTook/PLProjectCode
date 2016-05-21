import ast
from TypeBindingEnvironment import *

BuiltIns = ['print']

#The FunctionResolver class is responsible for resolving the possible types
#arguments of a function in the python source can be bound to, resolving the
#binding environment of the function body and resolving function dependencies.
class FunctionResolver(ast.NodeVisitor):
    #Class Constructor
    def __init__(self):
        self.typeResolver = None
        self.function = None
        self.returnNode = False
        self.returnVariables = []

    #Resolves a functions argument types.
    #Arguments:
    #   name: The function name.
    #   env: The root binding environment.
    #   node: The AST for a Call node
    def resolveArgumentTypes(self, name, env, node):
        self.function = env.find(name)
        args = self.visit(node)
        for i in range(0, len(args)):
            var = env.find(args[i])
            if isinstance(var, Variable):
                for t in var.types:
                    self.function.arguments[i].addType(t)
    
    #Resolves the binding environment of a function.
    #Arguments:
    #   name: The function name.
    #   env: The root binding environment.
    #   node: The AST for a FunctionDef node
    def resolveBindingEnvironment(self, name, env, node):
        self.function = env.find(name)

        self.typeResolver = TypeResolver()
        self.typeResolver.injectArguments(self.function.arguments)

        self.visit(node)
        self.function.environment = self.typeResolver.environment

        template = True
        for arg in self.function.arguments:
            if not(arg.name in self.returnVariables):
                template = False
                break
        self.function.template = template

    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        if self.returnNode and not(node.id in self.returnVariables):
            self.returnVariables.append(node.id)
        return node.id

    #--------------------------
    #-----Expression Nodes-----
    #--------------------------
    def visit_Call(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        return args

    #--------------------------
    #---Function/Class Nodes---
    #--------------------------
    def visit_FunctionDef(self, node):
        for expr in node.body:
            self.typeResolver.crawl(expr)
            if isinstance(expr, ast.Return):
                self.function.returnType = self.typeResolver.resolveReturnType(expr)
                self.returnNode = True
                self.visit(expr)
                self.returnNode = False

#The TypeResolver class is responsible for resolving the list of possible types
#each variable in the python source can be bound to. TypeResolve achieves this by doing
#an initial pass over the python source AST. Additionally TypeResolver can
#be used to resolve the type of a python expressions at translation time.
class TypeResolver(ast.NodeVisitor):
    #Class Constructor
    def __init__(self):
        self.environment = TypeBindingEnvironment()
        self.function = 'main'

    #Dumps the list of variables and their corresponding 
    #binding types to standard output.
    def dump(self):
        print('environment:')
        self.environment.dump(0)

    #Initializes the binding environment for a python source program.
    #Arguments:
    #   tree: The python source AST.
    def initialize(self, tree):
        self.crawl(tree)
        self.resolveFunctions(tree)

    #Crawls a AST to collect variable binding information.
    #Arguments:
    #   tree: The python source AST.
    def crawl(self, tree):
        self.visit(tree)

    #Injects function arguments into the environment.
    #Arguments:
    #   args: The Arguments.
    def injectArguments(self, args):
        for arg in args:
            self.environment.add(arg)

    #Gets the variables associated with the current binding environment.
    def getVariables(self):
        if self.function == 'main':
            env = self.environment
        else:
            env = self.environment.find(self.function).environment
        return env.variables

    #Resolves the argument type, local binding environment and dependencies
    #of a function.
    #Arguments:
    #   tree: The python source AST.
    def resolveFunctions(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = self.visit(node.func)
                if not(name in BuiltIns):
                    FunctionResolver().resolveArgumentTypes(name, self.environment, node)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not(node.name in BuiltIns):
                    FunctionResolver().resolveBindingEnvironment(node.name, self.environment, node)

    #Resolves the return type of a function.
    #Arguments:
    #   node: A AST return node.
    def resolveReturnType(self, node):
        return self.visit(node)

    #Resolves the type of a given variable. Note variables with 
    #multiple binding will be considered variants while variables
    #with only a single binding type will be considered that type.
    #Arguments:
    #   name: The variable name.
    #Returns:
    #   The variable type.
    def resolveVariableType(self, name):
        if self.function == 'main':
            env = self.environment
        else:
            env = self.environment.find(self.function).environment
        var = env.find(name)

        if isinstance(var, Function):
            return var.returnType
        elif len(var.types) > 1:
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
        if self.function == 'main':
            env = self.environment
        else:
            env = self.environment.find(self.function).environment

        for variable in variables:
            var = env.find(variable)
            if isinstance(var, Variable):
                var.boundType = primitiveType

    #Returns the type bound to the given variable.
    #Arguments:
    #   variable: The variable.
    def boundType(self, variable):
        if self.function == 'main':
            env = self.environment
        else:
            env = self.environment.find(self.function).environment

        var = env.find(variable)
        if isinstance(var, Variable):
            return var.boundType
        if isinstance(var, Function):
            return var.returnType

    #Retrieves a function from the binding environment.
    #Arguments:
    #   name: The function name.
    def retrieveFunction(self, name):
        return self.environment.find(name)
    
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
        if not(self.environment.contains(node.id)) and not(node.id in BuiltIns):
            self.environment.add(Variable(node.id))
        return node.id

    #------------------------
    #----Expression Nodes----
    #------------------------
    def visit_BinOp(self, node):
        leftType = self.visit(node.left)
        rightType = self.visit(node.right)

        if self.environment.contains(leftType):
            leftType = self.resolveVariableType(leftType)
        if self.environment.contains(rightType):
            rightType = self.resolveVariableType(rightType)

        if leftType == 'Variant' or rightType == 'Variant':
            return 'Variant'
        elif leftType == 'string' or rightType == 'string':
            return 'string'
        elif leftType == 'float' or rightType == 'float':
            return 'float'
        else:
            return 'int'

    def visit_BoolOp(self, node):
        return 'bool'

    def visit_NameConstant(self, node):
        return 'bool'

    def visit_Compare(self, node):
        return 'bool'

    def visit_UnaryOp(self, node):
        opType = self.visit(node.operand)
        if self.variableCollection.contains(opType):
            opType = self.resolveVariableType(opType)
        return opType

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        names = []
        for target in node.targets:
            names.append(self.visit(target))

        primitiveType = self.visit(node.value)

        for name in names:
            self.environment.find(name).addType(primitiveType)

    #--------------------------
    #---Function/Class Nodes---
    #--------------------------
    def visit_FunctionDef(self, node):
        name = str(node.name)
        self.environment.add(Function(name))

        args = self.visit(node.args)
        for arg in args:
            self.environment.find(name).addArgument(arg)

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        return args

    def visit_arg(self, node):
        return str(node.arg)

    def visit_Return(self, node):
        return self.visit(node.value)
