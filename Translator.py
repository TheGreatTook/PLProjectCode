import sys
import ast
from TypeResolver import *

#The Translator class is responsible for translating the pyton
#source code into valid C++ code.
class Translator(ast.NodeVisitor):
    #Class constructor
    def __init__(self):
        self.topNode = 'none'
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
        self.c_file.write('int main() {\n')

        self.visit(tree)

        self.c_file.write('  return 0;\n')
        self.c_file.write('}')

    #Insertes type casts for variables of type Variant. This is necessary 
    #because C++ requires the type of a variable to be know at compile time
    #When it is referenced.
    #Arguments:
    #   expr: An expression with references to variables of type Variant.
    #Returns:
    #   A new expression with the proper type casts inserted.
    def insertTypeCasts(self, expr):
        for var in self.typeResolver.variables:
            primitiveType = var.boundType
            if self.typeResolver.resolveVariableType(var.name) == 'Variant':
                expr = expr.replace(var.name, '(' + primitiveType + '&)' + var.name)
        return expr

    #Serialzes assignment expressions into c++ code.
    #Arguments:
    #   variables: The variables.
    #   value: The value.
    def serializeAssignment(self, variables, value):
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

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        self.topNode = 'Assign'

        variables = []
        for target in node.targets:
            variables.append(self.visit(target))
        
        value = self.insertTypeCasts(self.visit(node.value))
        self.serializeAssignment(variables, value)

        primitiveType = self.typeResolver.resolveExpressionType(node.value)
        self.typeResolver.updateBoundTypes(variables, primitiveType)

argc = len(sys.argv) - 1
argv = []
for i in range(1, len(sys.argv)):
    argv.append(sys.argv[i])

expr = open(argv[0], 'r').read()
tree = ast.parse(expr)
Translator().translate(tree)
