import ast
from TypeBindingEnvironment import *

#The TypeResolver class is responsible for resolving the list of possible types
#each variable in the python source can be bound to. TypeResolve achieves this by doing
#an initial pass over the python source AST. Additionally TypeResolver can
#be used to resolve the type of a python expressions at translation time.
class TypeResolver(ast.NodeVisitor):
    #Class Constructor
    def __init__(self):
        self.rootEnvironment = TypeBindingEnvironment()
        self.environment = self.rootEnvironment
        self.dependencies = {}

        self.callStack = ['main']
        self.c_types = ['int', 'double', 'string', 'bool', 'void', 'Variant']
        self.BuiltIns = ['print', 'range']
    
    #Initializes the root binding environment for a python source program.
    #Arguments:
    #   tree: The python source AST.
    def initialize(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit(node)
                self.dependencies[node.name] = self.scrapeDependencies(node.body)

        if len(self.dependencies.keys()) > 0:
            for k in self.dependencies.keys():
                key = k
                break
            self.resolveDependencies(key)

        self.visit(tree)
        self.environment.clearBindings()

    #Scrapes dependencies from a functions body.
    #Arguments:
    #   body: The function body.
    #Returns:
    #   A list containing the dependencies.
    def scrapeDependencies(self, body):
        dependencies = []
        for expr in body:
            for node in ast.iter_child_nodes(expr):
                if isinstance(node, ast.Call):
                    dependency = node.func.id
                    if not(dependency in self.BuiltIns):
                        dependencies.append(dependency)
        return dependencies

    #Resolves function dependencies.
    #Arguments:
    #   key: The key to the dictionary.
    def resolveDependencies(self, key):
        depends = self.dependencies[key]
        if len(depends) > 0:
            for depend in depends:
                if depend in self.dependencies.keys():
                    self.resolveDependencies(depend)

        if key in self.dependencies.keys():
            func = self.retrieveFunction(key)
            self.constructBindingEnvironment(func)
            del self.dependencies[key]
        
        if len(self.dependencies.keys()) > 0:
            for k in self.dependencies.keys():
                key = k
                break
            self.resolveDependencies(key)

    #Constructs the binding environment of a function.
    #Arguments:
    #   func: The function.
    def constructBindingEnvironment(self, func):
        self.pushFunction(func.name)

        for arg in func.arguments:
            self.environment.add(arg)

        for expr in func.body:
            if isinstance(expr, ast.Return):
                func.returnType = self.visit(expr)
            else:
                self.visit(expr)

        self.popFunction()

    #Pushes a function on to the call stack.
    #Arguments:
    #   func: The function to push.
    def pushFunction(self, func):
        self.callStack.append(func)
        self.updateEnvironment()

    #Pops a function off the top of the call stack.
    def popFunction(self):
        self.callStack.pop()
        self.updateEnvironment()

    #Updates the current binding environment.
    def updateEnvironment(self):
        func = self.callStack[-1]
        if self.rootEnvironment.contains(func):
            self.environment = self.rootEnvironment.find(func).environment
        else:
            self.environment = self.rootEnvironment

    #Gets the variable names associated with the current binding environment.
    #Returns:
    #   The variable names associated with the current binding environment.
    def getVariables(self):
        variables = []
        for elt in self.environment.elements:
            if isinstance(elt, Variable):
                variables.append(elt.name)
        return variables

    #Gets the function names associated with the root binding environment.
    #Returns:
    #   The function names associated with the current binding environment.
    def getFunctions(self):
        functions = []
        for elt in self.rootEnvironment.elements:
            if isinstance(elt, Function):
                functions.append(elt.name)
        return functions

    #Retrieves a function from the root binding environment.
    #Arguments:
    #   name: The function name.
    #Returns:
    #   The function.
    def retrieveFunction(self, name):
        return self.rootEnvironment.find(name)

    #Dumps the binding environment to standard output.
    def dump(self):
        print('environment:')
        self.environment.dump(0)

    #Updates the primitive type bound to the variables.
    #Arguments:
    #   variables: The variables to update.
    #   primitiveType: The primitiveType to bind.
    def bindType(self, variables, primitiveType):
        for variable in variables:
            var = self.environment.find(variable)
            var.boundType = primitiveType

    #Returns the type bound to the given variable.
    #Arguments:
    #   variable: The variable.
    #Returns:
    #   The bound type.
    def boundType(self, variable):
        var = self.environment.find(variable)
        return var.boundType

    #Checks if a type is a template.
    #Arguments:
    #   t: The type to check.
    #Returns:
    #   True if the type is a template. False otherwise.
    def isTemplate(self, t):
        if not(t in self.c_types):
            return True
        return False

    #Checks if a type is a CType.
    #Arguments:
    #   t: The type to check.
    #Returns:
    #   True if the type is a c_type. False otherwise
    def isCType(self, t):
        if t in self.c_types:
            return True
        return False

    #Resolves the return type of a function.
    #Arguments:
    #   name: The name of the function.
    #   argTypess: The argument types.
    def resolveReturnType(self, name, argTypes):
        self.pushFunction(name)

        func = self.retrieveFunction(name)
        for i in range(0, len(argTypes)):
            self.bindType([func.arguments[i].name], argTypes[i])

        for expr in func.body:
            if isinstance(expr, ast.Return):
                if self.isTemplate(func.returnType):
                    func.boundType = argTypes[0]
                else:
                    func.boundType = self.visit(expr)
            self.visit(expr)

        self.popFunction()

    #Resolves the type of a given variable. Note variables with 
    #multiple binding will be considered variants while variables
    #with only a single binding type will be considered that type.
    #Arguments:
    #   name: The variable name.
    #Returns:
    #   The variable type.
    def resolveVariableType(self, name):
        var = self.environment.find(name)
        if isinstance(var, Function):
            return var.returnType
        elif self.isTemplate(var.types[0]) and not(self.callStack[-1] == 'main'):
            return var.types[0]
        elif len(var.types) > 1 or self.isTemplate(var.types[0]):
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
    def resolveExpressionType(self, expr):
        primitiveType = self.visit(expr)
        if self.environment.contains(primitiveType):
            primitiveType = self.boundType(primitiveType)
        return primitiveType
    
    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    def visit_Num(self, node):
        value = str(node.n)
        for c in value:
            if c == '.':
                return 'double'
        return 'int'

    def visit_Str(self, node):
        return 'string'

    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        if not(self.environment.contains(node.id)) and not(node.id in self.BuiltIns) and not(node.id in self.getFunctions()):
            self.environment.add(Variable(node.id))
        return node.id

    #------------------------
    #----Expression Nodes----
    #------------------------
    def visit_BinOp(self, node):
        leftType = self.resolveExpressionType(node.left)
        rightType = self.resolveExpressionType(node.right)

        if leftType == 'void' or rightType == 'void':
            return 'void'
        elif self.isTemplate(leftType):
            return leftType
        elif self.isTemplate(rightType):
            return rightType
        elif leftType == 'Variant' and rightType == 'Variant':
            return 'Variant'
        elif leftType == 'string' or rightType == 'string':
            return 'string'
        elif leftType == 'double' or rightType == 'double':
            return 'double'
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
        if self.environment.contains(opType):
            opType = self.resolveVariableType(opType)
        return opType

    def visit_Call(self, node):
        name = self.visit(node.func)
        if name in self.getFunctions():
            func = self.retrieveFunction(name)
            if func.boundType == 'void':
                return func.returnType
            return func.boundType

    def visit_For(self, node):
        target = self.visit(node.target)
        if self.environment.contains(target):
            self.environment.find(target).addType('int')
        else:
            self.environment.add(Variable(node.id))
            self.environment.find(target).addType('int')
        for body in node.body:
            if isinstance(body, ast.Assign):
                name=''
                for field in ast.iter_child_nodes(body):
                    if isinstance(field, ast.Name):
                        name=self.visit(field)
                if self.environment.contains(name):
                    self.environment.find(name).addType('int')
                else:
                  self.environment.add(Variable(node.id))
                  self.environment.find(name).addType('int')

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        names = []
        for target in node.targets:
            names.append(self.visit(target))

        primitiveType = self.resolveExpressionType(node.value)
        for name in names:
            self.environment.find(name).addType(primitiveType)
            self.bindType([name], primitiveType)

    #--------------------------
    #---Function/Class Nodes---
    #--------------------------
    def visit_FunctionDef(self, node):
        if not(self.environment.contains(node.name)):
            func = Function(node.name)
            args = self.visit(node.args)
            for arg in args:
                func.addArgument(arg)
            func.body = node.body

            func.generateTemplateKeys()
            self.environment.add(func)

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        return args

    def visit_arg(self, node):
        return node.arg

    def visit_Return(self, node):
        return self.resolveExpressionType(node.value)
