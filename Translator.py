import sys
import re
import ast
from TypeResolver import *

class scopingHelper(ast.NodeVisitor):
    def __init__(self, TypeResolver):
        self.typeResolver = TypeResolver

    def visit_Name(self, node):
        return str(node.id)

    def visit_Assign(self, node):
        elementsToDeclare = []
        for target in node.targets:
            name = self.visit(target)
            if self.typeResolver.boundType(name) == 'void' and not (name in elementsToDeclare) :
                elementsToDeclare.append(name)
        return elementsToDeclare

#The Translator class is responsible for translating the pyton
#source code into valid C++ code.
class Translator(ast.NodeVisitor):
    #Class constructor
    def __init__(self):
        self.typeResolver = TypeResolver()
        self.translatedFunctions = []
        self.c_file = open('output.cpp', 'w')

    #Translates a python source AST into C++ code.
    #Arguments:
    #   tree: The python source AST.
    def translate(self, tree):
        self.typeResolver.initialize(tree)
        self.typeResolver.dump()

        self.c_file.write('#include "pylib.h"\n')
        self.c_file.write('#include <iostream>\n')
        self.c_file.write('#include <math.h>\n')
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
                self.forwardDeclaration(node)

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.visit(node)

    #Declares a function near the top of the c++ code.
    #Arguments:
    #   node: A FunctionDef AST node.
    def forwardDeclaration(self, node):
        self.serializeFunctionDeclaration(self.typeResolver.retrieveFunction(node.name), ';')
        self.c_file.write('\n')

    #Insertes type casts for variables of type Variant. This is necessary 
    #because C++ requires the type of a variable to be know at compile time
    #When it is referenced.
    #Arguments:
    #   expr: An expression with references to variables of type Variant.
    #Returns:
    #   A new expression with the proper type casts inserted.
    def insertTypeCasts(self, expr):
        tokens = re.findall("string\(.*\)|\S+", expr)
        for var in self.typeResolver.getVariables():
            primitiveType = self.typeResolver.boundType(var)
            if self.typeResolver.resolveVariableType(var) == 'Variant':
                cast = '(' + primitiveType + '&)' + var
                tokens = [cast if token == var else token for token in tokens]
        return ''.join(sum([[token, ' '] for token in tokens], [])[:-1])

    #Decorates the translated value string of an AST node 
    #with additional characters required in c++.
    #Arguments:
    #   node: The AST node whose translation should be decorated.
    #Returns:
    #   A decorated string.
    def decorate(self, node):
        value = self.visit(node)
        if isinstance(node, ast.Str):
            value = 'string(' + value + ')'
        return self.insertTypeCasts(value)

    #Serialzes an assignment expressions into c++ code.
    #Arguments:
    #   variables: The variables.
    #   value: The value.
    def serializeAssignment(self, variables, value):
        variants = []
        primitives = []
        for variable in variables:
            if self.typeResolver.boundType(variable) == 'void':
                variableType = self.typeResolver.resolveVariableType(variable)
                if variableType == 'Variant':
                    variants.append(variable)
                else:
                    primitives.append(variable)
        
        if len(variants) > 0:
            variantString = 'Variant ' + ''.join(sum([[var, ', '] for var in variants], [])[:-1])
            self.c_file.write('  ' + variantString + ';\n')
        if len(primitives) > 0:
            primitiveType = self.typeResolver.resolveVariableType(primitives[0]) + ' '
            primitiveString = primitiveType + ''.join(sum([[var, ', '] for var in primitives], [])[:-1])
            self.c_file.write('  ' + primitiveString + ';\n')
        if len(variables) > 0 and not(value == None):
            assignmentString = ''.join(sum([[var, ' = '] for var in variables], [])[:-1])
            self.c_file.write('  ' + assignmentString + ' = ' + value + ';\n')

    #Serialzes a function declaration expressions into c++ code.
    #Arguments:
    #   func: The function from the binding environment.
    #   postfix: The function string postfix.
    def serializeFunctionDeclaration(self, func, postfix):
        templates = []
        arguments = []
        for arg in func.arguments:
            templates.append(arg.types[0])
            arguments.append(arg.name)
        
        l1 = sum([[key, ' const & '] for key in templates], [])
        l2 = sum([[arg, ', '] for arg in arguments], [])[:-1]
        l2.append(')')
        l1 = [i+j for i,j in zip(l1[::2], l1[1::2])]
        l2 = [i+j for i,j in zip(l2[::2], l2[1::2])]

        returnString = func.returnType
        if self.typeResolver.isTemplate(func.returnType):
            returnString = 'inline ' + func.returnType + ' const &'
        templateString = 'template<typename ' + ''.join(sum([[key, ', typename '] for key in templates], [])[:-1]) + '>'
        functionString = returnString + ' ' + func.name + '(' + ''.join([val for pair in zip(l1, l2) for val in pair]) + postfix
        
        self.c_file.write(templateString + '\n')
        self.c_file.write(functionString + '\n')

    #Serializes a print function call into c++ code.
    #Arguments:
    #   args: The arguments.
    #Returns:
    #   A c++ cout statement.
    def serializePrint(self, args):
        return 'cout << ' + ''.join(sum([[self.decorate(arg), ' << '] for arg in args], [])) + 'endl'

    #Serializes a function call into c++ code.
    #Arguments:
    #   name: The function name.
    #   args: The arguments.
    #Returns:
    #   A c++ function call statement.
    def serializeCall(self, name, args):
        return name + '(' + ''.join(sum([[self.decorate(arg), ','] for arg in args], [])[:-1]) +')'

    #-----------------------
    #-----Literal Nodes-----
    #-----------------------
    def visit_Num(self, node):
        return str(node.n)

    def visit_Str(self, node):
        return '"' + node.s + '"'
    
    #-----------------------
    #-----Variable Node-----
    #-----------------------
    def visit_Name(self, node):
        return node.id

    #--------------------------
    #-----Expression Nodes-----
    #--------------------------
    def visit_Expr(self, node):
        self.c_file.write('  ' + self.visit(node.value) + ';\n')

    def visit_BinOp(self, node):
        op = self.visit(node.op)
        leftExpr = self.decorate(node.left)
        rightExpr = self.decorate(node.right)

        if op == '//':
            return 'floor(' + leftExpr + '/' + rightExpr +')'
        elif op == '%':
            return 'pMod(' + leftExpr + ',' + rightExpr + ')'
        elif op == '**':
            return 'pow(' + leftExpr + ',' + rightExpr + ')'
        else:
            return leftExpr + " " + op + " " + rightExpr

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
        op = self.visit(node.op)
        if op == "+":
            return self.visit(node.operand)
        if op == "-":
            return "-" + "(" + self.visit(node.operand) + ")"
        if op == "!":
            return "!" + "(" + self.visit(node.operand) + ")"

    def visit_UAdd(self, node):
        return "+"

    def visit_USub(self, node):
        return "-"
    
    def visit_Not(self, node):
        return "!"

    #Control Flow
    def visit_Return(self, node):
        value = self.visit(node.value)
        self.c_file.write('  return ' + value + ';\n')

    def visit_Break(self, node):
        return "break"

    def visit_Continue(self, node):
        return "continue"

    def visit_If(self, node):
        variables = []
        for element in node.body:
            if isinstance(element, ast.Assign):
                variables = scopingHelper(self.typeResolver).visit_Assign(element)
                self.typeResolver.bindTypes(variables, 'forwardDeclaration')
                self.serializeAssignment(variables, None)        
        self.c_file.write('  if(')
        self.c_file.write(self.visit(node.test) +')\n' + '  {' + '\n  ')  
        for i in range(0, len(node.body)):
            self.c_file.write('  ' + self.visit(node.body[i]) + ';\n')
        self.c_file.write('  } \n')
        if len(node.orelse) != 0:
            self.c_file.write("  else \n  { \n  " + self.visit((node.orelse[0])) + ';\n  } \n')

    def visit_While(self, node):
        variables = []
        for element in node.body:
            if isinstance(element, ast.Assign):
                variables = scopingHelper(self.typeResolver).visit_Assign(element)
                self.typeResolver.bindTypes(variables, 'forwardDeclaration')
                self.serializeAssignment(variables, None)
        self.c_file.write('  while (')
        self.c_file.write(self.visit(node.test) +')\n' + '  {' + '\n  ')  
        for i in range(0, len(node.body)):
            self.visit(node.body[i])
        self.c_file.write('  } \n')             

    def visit_Call(self, node):
        if self.visit(node.func) == 'print':
            return self.serializePrint(node.args)
        else:
            name = self.visit(node.func)
            argTypes = []
            for arg in node.args:
                argTypes.append(self.typeResolver.resolveExpressionType(arg))
            self.typeResolver.resolveReturnType(name, argTypes)

            return self.serializeCall(name, node.args)

    #-------------------------
    #-----Statement Nodes-----
    #-------------------------
    def visit_Assign(self, node):
        variables = []
        for target in node.targets:
            variables.append(self.visit(target))
        
        value = self.decorate(node.value)
        self.serializeAssignment(variables, value)

        primitiveType = self.typeResolver.resolveExpressionType(node.value)
        self.typeResolver.bindType(variables, primitiveType)
    
    #--------------------------
    #---Function/Class Nodes---
    #--------------------------
    def visit_FunctionDef(self, node):
        if not(node.name in self.translatedFunctions):
            self.typeResolver.pushFunction(node.name)

            self.translatedFunctions.append(node.name)
            self.serializeFunctionDeclaration(self.typeResolver.retrieveFunction(node.name), ' {')
            for expr in node.body:
                self.visit(expr)
            self.c_file.write('}\n\n')

            self.typeResolver.popFunction()

argc = len(sys.argv) - 1
argv = []
for i in range(1, len(sys.argv)):
    argv.append(sys.argv[i])

expr = open(argv[0], 'r').read()
tree = ast.parse(expr)
Translator().translate(tree)
