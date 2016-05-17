import ast
from TypeResolver import *


#The Translator class is responsible for translating the pyton
#source code into valid C++ code.
class Translator(ast.NodeVisitor):
    #Class constructor

    def __init__(self):
        self.typeResolver = TypeResolver()
        self.f = open('output.cpp', 'w')
        self.typeFloat = 0
        self.typeInt = 0

    #Translates a python source AST into C++ code.
    #Arguments:
    #   tree: The python source AST.
    def translate(self, tree):
        self.typeResolver.initialize(tree)
        self.typeResolver.dump()

        self.f.write('#include <iostream>\n')
        self.f.write('#include <string>\n')
        self.f.write('#include <math.h>\n')        
        self.f.write('using namespace std;\n\n')
        self.f.write('int main() {\n')

        self.visit(tree)

        self.f.write('  return 0;\n')
        self.f.write('}')

    #Insertes type casts for variables of type Variant. This is necessary 
    #because C++ requires the type of a variable to be know at compile time
    #When it is referenced.
    #Arguments:
    #   expr: An expression with references to variables of type Variant.
    #Returns:
    #   A new expression with the proper type casts inserted.
    def insertTypeCasts(self, expr):
        for var in self.typeResolver.boundVariables.variables:
            primitiveType = self.typeResolver.boundVariables.apply(var)
            if not(primitiveType == None) and self.typeResolver.resolveVariableType(var) == 'Variant':
                expr = expr.replace(var, '(' + primitiveType + '&)' + var)
        return expr

    def serializeVars_Declaration(self, variants, primitives):
        vStr = ''
        vCount = 0
        count = 0
        for variant in variants:
            count += 1
            if not(self.typeResolver.boundVariables.contains(variant[0])):
                vStr += variant[0]
                vCount += 1
            if count != len(variants):
                vStr += ', '

        pStr = ''
        pCount = 0
        count = 0
        for primitive in primitives:
            count += 1
            if not(self.typeResolver.boundVariables.contains(primitive[0])):
                pStr += primitive[0]
                pCount += 1
            if count != len(primitives):
                pStr += ', '

        return ((vStr, vCount), (pStr, pCount))

    def serializeVars_Assignment(self, variants, primitives):
        vStr = ''
        count = 0
        for variant in variants:
            count += 1
            vStr += variant[0]
            if count != len(variants):
                vStr += ' = '

        pStr = ''
        count = 0
        for primitive in primitives:
            count += 1
            pStr += primitive[0]
            if count != len(primitives):
                pStr += ' = '

        aStr = ''
        aStr = aStr + vStr
        if vStr != '' and pStr != '':
            aStr = aStr + ' = '
        aStr = aStr + pStr

        return aStr

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
        variants = []
        primitives = []
        for target in node.targets:
            name = self.visit(target)
            t = self.typeResolver.resolveVariableType(name)
            if t == 'Variant':
                variants.append((name, t))
            else:
                primitives.append((name, t))

        value = self.visit(node.value)
        primitiveType = self.typeResolver.resolveExpressionType(value)

        value = self.insertTypeCasts(value)

        if(self.typeInt == 1):
            self.typeInt -= 1
            primitiveType = 'int'
        elif(self.typeFloat == 1):
            self.typeFloat -= 1
            primitiveType = 'float'
        dStrs = self.serializeVars_Declaration(variants, primitives)
        aStr = self.serializeVars_Assignment(variants, primitives)
        if len(variants) + len(primitives) == 1:
            if dStrs[0][1] != 0:
                self.f.write('  ' + 'Variant' + ' ' + dStrs[0][0] + ' = ' + value + ';\n')
            elif dStrs[1][1] != 0:
                self.f.write('  ' + primitiveType + ' ' + dStrs[1][0] + ' = ' + value + ';\n')
            else:
                self.f.write('  ' + aStr + " = " + value + ';\n')
        else:
            if dStrs[0][1] != 0:
                self.f.write('  ' + 'Variant' + ' ' + dStrs[0][0] + ';\n')
            if dStrs[1][1] != 0:
                self.f.write('  ' + primitiveType + ' ' + dStrs[1][0] + ';\n')
            self.f.write('  ' + aStr + " = " + value + ';\n')

        self.typeResolver.updateBoundVars(variants, primitives, primitiveType)

    def visit_Print(self, node):
        self.f.write('  cout << ' + self.insertTypeCasts(self.visit(node.values[0])) + ' << endl;\n')

expr = """
a=b=1+1.5*2
c=a+b
d="test"
print(d)
e=b=3
print(b)
a="hello world"
g=True
h=b<c
i=True
print(a)
k=e**b
j=g and i
if (g and i):
    return j
else:
    return i
f=c+e
while (i):
    return j

"""


expr2= """
print("hello world")"""


tree = ast.parse(expr)
print(ast.dump(tree))
print(" ")
#print(ast.dump(ast.parse(expr2)))
Translator().translate(tree)
