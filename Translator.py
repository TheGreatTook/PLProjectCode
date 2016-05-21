import sys
import ast
from TypeResolver import *


#The Translator class is responsible for translating the pyton
#source code into valid C++ code.
class Translator(ast.NodeVisitor):
    #Class constructor

    def __init__(self):
        self.typeResolver = TypeResolver()
        self.c_file = open('output.cpp', 'w')

    #Translates a python source AST into C++ code.
    #Arguments:
    #   tree: The python source AST.
    def translate(self, tree):
        self.typeResolver.initialize(tree)
        self.typeResolver.dump()

        self.c_file.write('#include <iostream>\n')
        self.c_file.write('#include <math.h>\n')
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

    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        return 'string("' + str(node.s) + '")'
    
    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        return str(node.id)

    #--------------------------
    #-----Expression Nodes-----
    #--------------------------
    def visit_BinOp(self, node):
        if(self.visit(node.op) == '//'):
            self.typeInt += 1
            return 'floor(' + self.visit(node.left) + '/' + self.visit(node.right) +')'
        elif(self.visit(node.op) == '%'):
            self.typeInt += 1
            return 'pMod(' + self.visit(node.left) + ',' + self.visit(node.right) + ')'
        elif(self.visit(node.op) == '**'):
            self.typeFloat +=1
            return 'pow(' + self.visit(node.left) + ',' + self.visit(node.right) + ')'
        else:
            return self.visit(node.left) + " " + self.visit(node.op) + " " + self.visit(node.right)


    def visit_Add(self, node):
        return '+'

    def visit_Sub(self, node):
        return '-'

    def visit_Mult(self, node):
        return '*'

    def visit_Div(self, node):
        return '/'

    def visit_FloorDiv(self, node):
        return '//'

    def visit_Mod(self, node):
        return '%'

    def visit_Pow(self, node):
        return '**'

    def visit_LShift(self, node):
        return '<<'

    def visit_RShift(self, node):
        return '>>'

    def visit_BitOr(self, node):
        return '|'

    def visit_BitXor(self, node):
        return '^'

    def visit_BitAnd(self, node):
        return '&'

    #boolean stuff
    def visit_BoolOp(self, node):
        boolString = ''
        for i in range (0, len(node.values)):
            if(i != len(node.values)-1):
                boolString += self.visit(node.values[i]) + " " + self.visit(node.op) + " "
            else:
                boolString += self.visit(node.values[i])
        return boolString

    def visit_And(self, node):
        return 'and'

    def visit_Or(self, node):
        return 'or'

    def visit_NameConstant(self, node): 
        return str(node.value)

    #compare stuff
    def visit_Compare(self, node):
         compareString = self.visit(node.left)
         for i in range (0, len(node.ops)): 
            compareString += " " + self.visit(node.ops[i]) + " " + self.visit(node.comparators[i]) + " "
         return compareString

    def visit_Eq(self, node):
        return '='


    def visit_NotEq(self, node):
        return '!='        


    def visit_Lt(self, node):
        return '<'


    def visit_LtE(self, node):
        return '<='


    def visit_Gt(self, node):
        return '>'


    def visit_GtE(self, node):
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

    #Control Flow
    def visit_Return(self, node):
        return "return "+ self.visit(node.value)

    def visit_Break(self, node):
        return "break"

    def visit_Continue(self, node):
        return "continue"

    def visit_If(self, node):

        self.f.write('  if(')
        self.f.write(self.visit(node.test) +')\n' + '  {' + '\n  ')  
        for i in range(0, len(node.body)):
            self.f.write(self.visit(node.body[i]) + ';\n')
        self.f.write('  } \n')
        if len(node.orelse) != 0:
            self.f.write("  else \n  { \n  " + self.visit((node.orelse[0])) + ';\n  } \n')

    def visit_While(self, node):
        self.f.write('  while (')
        self.f.write(self.visit(node.test) +')\n' + '  {' + '\n  ')  
        for i in range(0, len(node.body)):
            self.f.write(self.visit(node.body[i]) + ';\n')
        self.f.write('  } \n')        

    #Statement Nodes

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        variables = []
        for target in node.targets:
            variables.append(self.visit(target))
        
        value = self.insertTypeCasts(self.visit(node.value))
        self.serializeAssignment(variables, value)

        primitiveType = self.typeResolver.resolveExpressionType(node.value)
        self.typeResolver.updateBoundTypes(variables, primitiveType)


    def visit_Print(self, node):

        self.c_file.write('  cout << ' + self.insertTypeCasts(self.visit(node.values[0])) + ' << endl;\n')

        argc = len(sys.argv) - 1
        argv = []
        for i in range(1, len(sys.argv)):
            argv.append(sys.argv[i])

        testExpr = open(argv[0], 'r').read()
        print(testExpr)






expr = """
a=b=1+1.5*2
c=a+b
d="test"
print(d)
e=b=3
print(b)
a="hello world"
print(a)
f=c+e
"""

expr2= """
print("hello world")
a=1
b=2
a<b
"""

expr3= """
print(b)
!b
+b
-a
"""

tree = ast.parse(expr)
Translator().translate(tree)
