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

        self.c_types = ['int', 'double', 'string', 'bool', 'Variant']
        self.BuiltIns = ['print']
    
    #Initializes the root binding environment for a python source program.
    #Arguments:
    #   tree: The python source AST.
    def initialize(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit(node)
        self.visit(tree)
        self.environment.clearBindings()

    #Creates a template generator closure.
    #Arguments:
    #   templates: A list of template keys.
    #Returns:
    #   A unqiue template key.
    def makeTemplateGenerator(self, templates):
        count = [0]
        def generateTemplate():
            key = ''
            repeat = (count[0] // len(templates)) + 1
            for i in range(0, repeat):
                key += templates[count[0] % len(templates)]
            count[0] += 1
            return key
        return generateTemplate

    #Generates the function argument template keys.
    #Arguments:
    #   func: The function.
    def generateTemplateKeys(self, func):
        generate = self.makeTemplateGenerator(['T', 'U', 'V', 'W'])
        for arg in func.arguments:
            arg.types = [generate()]
            arg.boundType = arg.types[0]

    #Constructs the binding environment of a function.
    #Arguments:
    #   func: The function.
    def constructBindingEnvironment(self, func):
        self.setEnvironment(func.name)

        for arg in func.arguments:
            self.environment.add(arg)

        for expr in func.body:
            if isinstance(expr, ast.Return):
                func.returnType = self.visit(expr)
            else:
                self.visit(expr)

        self.setEnvironment('main')

    #Sets the current binding environment.
    #Arguments:
    #   func: The function whose binding environment we should use.
    def setEnvironment(self, func):
        if self.rootEnvironment.contains(func):
            self.environment = self.rootEnvironment.find(func).environment
        else:
            self.environment = self.rootEnvironment

    #Gets the variable names associated with the current binding environment.
    #Returns:
    #   The variables associated with the current binding environment.
    def getVariables(self):
        variables = []
        for elt in self.environment.elements:
            if isinstance(elt, Variable):
                variables.append(elt.name)
        return variables

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
    #Returns:
    #   The functions return type.
    def resolveReturnType(self, name, argTypes):
        self.setEnvironment(name)

        func = self.retrieveFunction(name)
        for i in range(0, len(argTypes)):
            self.bindType([func.arguments[i].name], argTypes[i])

        for expr in func.body:
            if isinstance(expr, ast.Return):
                func.boundType = self.visit(expr)
            self.visit(expr)

        self.setEnvironment('main')

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
        primitiveType = self.visit(node)
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
        if not(self.environment.contains(node.id)) and not(node.id in self.BuiltIns):
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
        #elif self.isTemplate(leftType) and self.isTemplate(rightType):
            #return 'Variant'
        elif self.isTemplate(leftType):
            return leftType
        elif self.isTemplate(rightType):
            return rightType
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
        if self.environment.contains(name):
            func = self.environment.find(name)
            if func.boundType == 'void':
                return func.returnType
            return func.boundType

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

            self.environment.add(func)
            self.generateTemplateKeys(func)
            self.constructBindingEnvironment(func)

    def visit_arguments(self, node):
        args = []
        for arg in node.args:
            args.append(self.visit(arg))
        return args

    def visit_arg(self, node):
        return node.arg

    def visit_Return(self, node):
        t = self.visit(node.value)
        if self.isTemplate(t):
            return 'Variant'
        return t
