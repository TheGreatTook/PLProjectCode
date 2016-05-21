import sys
import ast
from TypeResolver import *

#The Translator class is responsible for translating the pyton
#source code into valid C++ code.
class Translator(ast.NodeVisitor):
    #Class constructor
    def __init__(self):
        self.topNode = 'none'
        self.translatedFunctions = []
        self.typeResolver = TypeResolver()
        self.c_file = open('output.cpp', 'w')

    #Translates a python source AST into C++ code.
    #Arguments:
    #   tree: The python source AST.
    def translate(self, tree):
        self.typeResolver.initialize(tree)
        self.typeResolver.dump()

        self.c_file.write('#include <iostream>\n')
        self.c_file.write('#include <string>\n')
        self.c_file.write('using namespace std;\n\n')

        self.translateFunctions(tree)

        self.c_file.write('int main() {\n')
        self.visit(tree)
        self.c_file.write('  return 0;\n')
        self.c_file.write('}')

    #Translates all functions up front.
    #Arguments:
    #   tree: The python source AST.
    def translateFunctions(self, tree):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit(node)
    
    #Tokenizes a string.
    #Arguments:
    #   string: The string to tokenize.
    def tokenize(self, string):
        inString = False
        tokens = []
        simpleTokens = string.split()
        complexToken = ''
        for token in simpleTokens:
            if not(inString):
                complexToken = token
            else:
                complexToken += ' ' + token

            if token.startswith('string("'):
                inString = True
            if token.endswith('")'):
                inString = False

            if not(inString):
                tokens.append(complexToken)
                complexToken = ''
        return tokens

    #Insertes type casts for variables of type Variant. This is necessary 
    #because C++ requires the type of a variable to be know at compile time
    #When it is referenced.
    #Arguments:
    #   expr: An expression with references to variables of type Variant.
    #Returns:
    #   A new expression with the proper type casts inserted.
    def insertTypeCasts(self, expr):
        tokens = self.tokenize(expr)
        for var in self.typeResolver.getVariables():
            primitiveType = self.typeResolver.boundType(var.name)
            if self.typeResolver.resolveVariableType(var.name) == 'Variant':
                for i in range(0, len(tokens)):
                    if tokens[i] == var.name:
                        tokens[i] = '(' + primitiveType + '&)' + var.name

        newExpr = tokens[0]
        for i in range(1, len(tokens)):
            newExpr += ' ' + tokens[i]
        return newExpr

    #Serialzes a variable assignment expressions into c++ code.
    #Arguments:
    #   variables: The variables.
    #   value: The value.
    def serializeAssignment_Variable(self, variables, value):
        variantLine = ''
        variantCount = 0

        primitiveLine = ''
        primitiveCount = 0

        assignmentLine = ''

        for variable in variables:
            if self.typeResolver.boundType(variable) == 'void':
                variableType = self.typeResolver.resolveVariableType(variable)
                if variableType == 'Variant':
                    if variantCount == 0:
                        variantLine += variableType + ' '  + variable
                    else:
                        variantLine += ', ' + variable
                    variantCount += 1
                else:
                    if primitiveCount == 0:
                        primitiveLine += variableType + ' ' + variable
                    else:
                        primitiveLine += ', ' + variable
                    primitiveCount += 1
            assignmentLine += variable + ' = '

        if variantCount + primitiveCount == 1 and len(variables) == 1:
            if variantCount == 1:
                variantLine += ' = ' + value
            else:
                primitiveLine += ' = ' + value
            assignmentLine = ''

        if not(variantLine == ''):
            self.c_file.write('  ' + variantLine + ';\n')
        if not(primitiveLine == ''):
            self.c_file.write('  ' + primitiveLine + ';\n')
        if not(assignmentLine == ''):
            self.c_file.write('  ' + assignmentLine + value + ';\n')

    #Serialzes a function assignment expressions into c++ code.
    #Arguments:
    #   func: The function from the binding environment.
    def serializeAssignment_Function(self, func):
        templates = ['T', 'U', 'V', 'W']
        templateLine = 'template <'
        templateCount = 0

        functionLine = func.name + '('
        argumentCount = 0
        for arg in func.arguments:
            if argumentCount > 0:
                functionLine += ', '
            if len(arg.types) > 1:
                if templateCount > 0:
                   templateLine += ', ' 
                templateLine += 'typename ' + templates[templateCount]
                functionLine += templates[templateCount] + ' const & ' + arg.name
                templateCount += 1
            else:
                functionLine += arg.types[0] + ' ' + arg.name
            argumentCount += 1

        templateLine += '>'
        if func.template:
            functionLine = 'inline ' + templates[0] + ' const & ' + functionLine + ') {'
        
        if templateCount > 0:
            self.c_file.write(templateLine + '\n')
        self.c_file.write(functionLine + '\n')

    #Serializes print function call into c++ code.
    #Arguments:
    #   args: The arguments.
    def serializePrint(self, args):
        coutLine = '  cout << '
        for arg in args:
            coutLine += self.insertTypeCasts(self.visit(arg)) + ' << '
        coutLine += 'endl;\n'
        self.c_file.write(coutLine)

    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        if self.topNode == 'Assign':
            return 'string("' + str(node.s) + '")'
        return str('"' + node.s + '"')
    
    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        return str(node.id)

    #--------------------------
    #-----Expression Nodes-----
    #--------------------------
    def visit_BinOp(self, node):
        leftExpr = self.visit(node.left)
        rightExpr = self.visit(node.right)
        return self.visit(node.left) + " " + self.visit(node.op) + " " + self.visit(node.right)

    def visit_Add(self, node):
        return '+'

    def visit_Sub(self, node):
        return '-'

    def visit_Mult(self, node):
        return '*'

    def visit_Div(self, node):
        return '/'

    #boolean stuff
    def vist__BoolOp(self, node):
        return self.visit(node.left) + " " + self.visit(node.op) + " " + self.visit(node.right)

    def visit_And(self, node):
        return "and"

    def visit_Or(self, node):
        return "or"

    #compare stuff
    def visit_Compare(self, node):
         return self.visit(node.left) + " " + self.visit(node.op) + " " + self.visit(node.right)

    def vist_Eq(self, node):
        return '='

    def vist_NotEq(self, node):
        return '!='        

    def vist_Lt(self, node):
        return '<'

    def vist_LtE(self, node):
        return '<='

    def vist_Gt(self, node):
        return '>'

    def vist_GtE(self, node):
        return '>='


    #Unary Nodes
    #not including Invert because doing 2's complement math in Python seems like a waste of time

    def visit_UnaryOp(self, node):
        return self.visit(node.op) + self.visit(node.operand)

    def visit_UAdd(self, node):
        return '++'

    def visit_uSub(self, node):
        return '--'

    def visit_Not(self, node):
        return '!'

    def visit_Call(self, node):
        self.topNode = 'Call'

        if self.visit(node.func) == 'print':
            self.serializePrint(node.args)
        else:
            callLine = ''
            callLine += self.visit(node.func) + '('
            for i in range(0, len(node.args)):
                if i > 0:
                    callLine += ', '
                callLine += self.insertTypeCasts(self.visit(node.args[i]))
            callLine += ')'
            self.c_file.write('  ' + callLine + ';\n')

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        self.topNode = 'Assign'

        variables = []
        for target in node.targets:
            variables.append(self.visit(target))
        
        value = self.insertTypeCasts(self.visit(node.value))
        self.serializeAssignment_Variable(variables, value)

        primitiveType = self.typeResolver.resolveExpressionType(node.value)
        self.typeResolver.updateBoundTypes(variables, primitiveType)
    
    #--------------------------
    #---Function/Class Nodes---
    #--------------------------
    def visit_FunctionDef(self, node):
        if not(node.name in self.translatedFunctions):
            self.typeResolver.function = node.name

            self.translatedFunctions.append(node.name)
            self.serializeAssignment_Function(self.typeResolver.retrieveFunction(node.name))
            for expr in node.body:
                self.visit(expr)
            self.c_file.write('}\n\n')

            self.typeResolver.function = 'main'

    def visit_Return(self, node):
        value = self.visit(node.value)
        self.c_file.write('  return ' + value + ';\n')

argc = len(sys.argv) - 1
argv = []
for i in range(1, len(sys.argv)):
    argv.append(sys.argv[i])

expr = open(argv[0], 'r').read()
tree = ast.parse(expr)
Translator().translate(tree)
