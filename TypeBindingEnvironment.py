#The Function class is a data structure representing a function
#in the python source. It contains the name of a function along with
#all the typing information associated with that function.
#Function's are stored in the type binding environment.
class Function():
    def __init__(self, name):
        self.name = name
        self.arguments = []
        self.environment = TypeBindingEnvironment()
        self.body = None
        self.returnType = 'void'
        self.boundType = 'void'

    #Adds an argument to argument the collection.
    #Arguments:
    #   name: The name of the argument.
    def addArgument(self, name):
        self.arguments.append(Variable(name))

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

    #Generates the argument template keys.
    def generateTemplateKeys(self):
        generate = self.makeTemplateGenerator(['T', 'U', 'V', 'W'])
        for arg in self.arguments:
            arg.types = [generate()]
            arg.boundType = arg.types[0]

#The Variable class is a data structure representing a variable
#in the python source. It contains the name of a variable along with
#all the typing information associated with that variable.
#Variable's are stored in the type binding environment.
class Variable():
    def __init__(self, name):
        self.name = name
        self.types = []
        self.boundType = 'void'
    
    #Adds a type to the type collection.
    #Arguments:
    #   t: The type to add.
    def addType(self, t):
        if not(t in self.types):
            self.types.append(t)

#The TypeBindingEnvironment class is a data structure that holds
#all the relevant typing information for every variable and function
#found in the python source. The TypeBindingEnvironment is used by
#the type resolver at translation time to retrieve the appropriate typing 
#information associated with variables and functions.
class TypeBindingEnvironment():
    def __init__(self):
        self.elements = []

    #Gets the size of the binding environment.
    #Returns:
    #   The size of the binding environment.
    def size(self):
        return len(self.elements)

    #Determines if the binding environment contains an element.
    #Arguments:
    #   name: The element name.
    #Returns:
    #   True if the element is in the binding environment. False otherwise.
    def contains(self, name):
        for elt in self.elements:
            if elt.name == name:
                return True
        return False

    #Finds an element in the binding environment.
    #Arguments:
    #   name: The element name.
    #Returns:
    #   The element if it exists. None otherwise.
    def find(self, name):
        for elt in self.elements:
            if elt.name == name:
                return elt
        return None

    #Adds a element to the binding environment.
    #Arguments:
    #   elt: The element to add.
    def add(self, elt):
        self.elements.append(elt)

    #Clears all the bindings in the binding environment.
    def clearBindings(self):
        for elt in self.elements:
            elt.boundType = 'void'
            if isinstance(elt, Function):
                elt.environment.clearBindings()
                for arg in elt.arguments:
                    arg.boundType = arg.types[0]

    #Dumps the binding environment to standard output.
    def dump(self, offset):
        prefix = ''
        for i in range(0, offset):
            prefix += '>>'

        print(prefix + '-----------------------------------')
        for elt in self.elements:
            if isinstance(elt, Variable):
                print(prefix + elt.name, '{', elt.types, elt.boundType, '}')
            if isinstance(elt, Function):
                print(prefix + elt.name, '{')
                print(prefix + 'arguments:')
                for arg in elt.arguments:
                    print(prefix + '>>' + arg.name, arg.types, arg.boundType)
                print(prefix + 'environment:')
                elt.environment.dump(offset + 1)
                print(prefix + 'returns:')
                print(prefix + '>>' + elt.returnType)
                print(elt.boundType, '}')
        print(prefix + '-----------------------------------')
