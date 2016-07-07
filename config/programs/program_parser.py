from shlex import shlex

class TaskCall(object):
    def __init__(self):
        self.commandName = ''
        self.paramFormat = ''
        self.paramList = ''
        self.returnValue = ''

class TaskExpression(object):
    def __init__(self):
        self.varName = ''
        self.rValue = ''

class Task(object):
    def __init__(self):
        self.variables = []
        self.loopCommands = []
        self.setupCommands = []

class TaskParser(object):


    class LinearBlock:
        def __init__(self):
            self.contained = []

    class FunctionBlock:
        def __init__(self, name):
            self.name = name
            self.arglist = {}
            self.contained = []

        def addStatement(self, s):
            self.contained.append(s)

    class IfThenElseBlock:
        def __init__(self):
            self.branches = {}

        def addCondition(conditionStr=None, consequence=[]):
            if conditionStr not in self.branches:
                self.branches[conditionStr] = consequence

    def isReservedWord(self, word):
        if word in self.builtinFunctions:
            return True
        if word in self.allowedFunctions:
            return True
        if word in self.typeNames:
            return True
        return False
     
    builtinFunctions = ['sensorValue', 'actuatorCommand', 'findActuator', 'findSensor']
    typeNames = ['num', 'string']
    ###  --------------------------
    def __init__(self):
        self.braceDepth = 0
        self.context = []
        self.functionBlocks = []
        self.allowedFunctions = ['setup', 'loop']

    def parseArgList(self, lims='()'):
        tok = self.lexer.get_token()
        elems = {}
        finished = False
        if tok != lims[0]:
            raise ValueError
        while tok != self.lexer.eof:
            tok1 = self.lexer.get_token()
            if tok1 == ')':
                finished = True
                break
            tok2 = self.lexer.get_token()
            if (tok1 == ',' or tok2 == ','):
                raise ValueError
            elems[tok2] = tok1
            tok = self.lexer.get_token()
            if tok == lims[1]:
                finished = True
                break
            elif tok != ',':
                raise ValueError
        if not finished:
            raise ValueError
        return elems

    def loadTaskFromFile(self, filename):
        if filename is not None:
            self.filestream = open(filename, 'r')
            self.lexer = shlex(self.filestream, filename)
        else:
            self.lexer = shlex()
        theTask = Task()
        
        tok = self.lexer.get_token()
        while tok != self.lexer.eof:
            try:
                if len(self.context) == 0:
                    # we need to be starting a function
                    if (tok != 'func'):
                        raise ValueError('Missing function at line {}: got {}'.format(self.lexer.lineno, tok))
                    else:
                        tok = self.lexer.get_token()
                        if tok not in self.allowedFunctions:
                            raise ValueError('Bad function name at line {}: got {}, expected: {}'.format(self.lexer.lineno, tok, ' or '.join(self.allowedFunctions)))
                        # todo: make sure function name doesnt have weird crap in it
                        f = self.FunctionBlock(tok)

                        ## put this back when custom functions are allowed
                        ## parse parenthesized list and then a {
                        #listVals = self.parseArgList('()')
                        #f.arglist = listVals
                        tok = self.lexer.get_token()
                        if tok != '{':
                            raise ValueError('Expected function body start at line {}, got {}'.format(self.lexer.lineno, tok))
                        self.context.append(f)
                        # we have entered the function body
                else:
                    currentContext = self.context[-1]
                    if isinstance(currentContext, self.FunctionBlock):
                        if tok == '}':
                            # end of function
                            self.context.pop()
                        else:
                            # let's see what's in this function
                            if tok in self.typeNames:
                                tok 

                            currentContext.contained.append(tok)
                        
                tok = self.lexer.get_token()
                    
            except ValueError as e:
                print 'PARSE ERROR: ', e.message, self.context
                break # should we print an error message?
                
if __name__ == '__main__':
    k = TaskParser()
    k.loadTaskFromFile(None)