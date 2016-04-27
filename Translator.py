import ast
from TypeResolver import *

class Translator(ast.NodeVisitor):
    def __init__(self):
        self.typeResolver = TypeResolver()
        self.f = open('output.cpp', 'w')

    def translate(self, tree):
        self.typeResolver.initialize(tree)
        self.typeResolver.dump()

        self.f.write('#include <iostream>\n')
        self.f.write('#include <string>\n')
        self.f.write('using namespace std;\n\n')
        self.f.write('int main() {\n')

        self.visit(tree)

        self.f.write('  return 0;\n')
        self.f.write('}')

    #Helper Methods
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

    #Literal Nodes
    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        return 'string("' + str(node.s) + '")'
    
    #Variable Node
    def visit_Name(self, node):
        return str(node.id)

    #Expression Nodes
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

    def vist__BoolOp(self, node):
        return self.visit(node.left) + " " + self.visit(node.op) + " " + self.visit(node.right)

    def visit_And(self, node):
        return "and"

    def visit_Or(self, node):
        return "or"

    #Statement Nodes
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
print(a)
f=c+e
"""

tree = ast.parse(expr)
print(ast.dump(tree))
Translator().translate(tree)
