from enum import Enum, auto
from lexurgy_scanner import Lexer, Tokens

# state enumerator
class State(Enum):
    START = auto()
    FEATURELIST = auto()
    SYMBOLLIST = auto()
    RULELIST = auto()
    FEATURE = auto()
    SYMBOL = auto()
    COMMAIDLIST = auto()
    COMMAIDLIST1 = auto()
    COMMAIDLIST2 = auto()
    IDLIST = auto()
    IDLIST1 = auto()
    RULE = auto()
    RULE1 = auto()
    EXPR = auto()
    EXPR1 = auto()
    ARG = auto()
    ENVIRON = auto()
    NEGENVIRON = auto()
    REDUCE = auto()
    
    def __str__(self):
        return self.name
    
    def type(self):
        return 'non-term'


class Reduce:
    def __init__(self, state, count):
        self.state = state
        self.count = count
    def __str__(self):
        return f'{self.state}: {self.count} items'
    
class Folder:
    def __init__(self, state, lexeme="", lineno=0):
        self.state = state
        self.items = []
        self.lexeme = lexeme
        self.lineno = lineno
        
    def copy(self):
        x = Folder(self.state, self.lexeme, self.lineno)
        x.items.extend(self.items)
        return x
        
    def print_foldr(self, tab=0):
        print((" " * tab * 4) + str(self.state) + ": " + self.lexeme)
        i = len(self.items) - 1
        while i >= 0:
            self.items[i].print_foldr(tab+1)
            i -= 1

class Parser:
    def __init__(self, mylex: Lexer):
        self.table = {}
        self.lexer = mylex
        self.stack = []
        self.root = 0
        self.value_stack = []
        self.final = None
    
    def prime_table(self):
        self.table = {
            # starting state
            (State.START, Tokens.FEATURE) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.SYMBOL) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.ID) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.UNDERSCORE) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.ASTERISK) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.LBRACKET) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.DOLLAR) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            (State.START, Tokens.EOF) : [State.FEATURELIST, State.SYMBOLLIST, State.RULELIST],
            
            # featurelist state
            (State.FEATURELIST, Tokens.FEATURE) : [State.FEATURE, State.FEATURELIST],
            (State.FEATURELIST, Tokens.SYMBOL) : [],
            (State.FEATURELIST, Tokens.ID) : [],
            (State.FEATURELIST, Tokens.UNDERSCORE) : [],
            (State.FEATURELIST, Tokens.ASTERISK) : [],
            (State.FEATURELIST, Tokens.LBRACKET) : [],
            (State.FEATURELIST, Tokens.DOLLAR) : [],
            (State.FEATURELIST, Tokens.EOF) : [],
            
            # symbollist state
            (State.SYMBOLLIST, Tokens.SYMBOL) : [State.SYMBOL, State.SYMBOLLIST],
            (State.SYMBOLLIST, Tokens.ID) : [],
            (State.SYMBOLLIST, Tokens.UNDERSCORE) : [],
            (State.SYMBOLLIST, Tokens.ASTERISK) : [],
            (State.SYMBOLLIST, Tokens.LBRACKET) : [],
            (State.SYMBOLLIST, Tokens.DOLLAR) : [],
            (State.SYMBOLLIST, Tokens.EOF) : [],
            
            # rulelist state
            (State.RULELIST, Tokens.ID) : [State.RULE, State.RULELIST],
            (State.RULELIST, Tokens.UNDERSCORE) : [State.RULE, State.RULELIST],
            (State.RULELIST, Tokens.ASTERISK) : [State.RULE, State.RULELIST],
            (State.RULELIST, Tokens.LBRACKET) : [State.RULE, State.RULELIST],
            (State.RULELIST, Tokens.DOLLAR) : [State.RULE, State.RULELIST],
            (State.RULELIST, Tokens.EOF) : [],
            
            # feature state
            (State.FEATURE, Tokens.FEATURE) : [Tokens.FEATURE, Tokens.ID, State.COMMAIDLIST, Tokens.SEMICOLON],
            
            # symbol state
            (State.SYMBOL, Tokens.SYMBOL) : [Tokens.SYMBOL, Tokens.ID, State.IDLIST, Tokens.SEMICOLON],
            
            # commaidlist state
            (State.COMMAIDLIST, Tokens.LPARENTH) : [Tokens.LPARENTH, State.COMMAIDLIST1, Tokens.RPARENTH],
            
            # commaidlist1 state
            (State.COMMAIDLIST1, Tokens.ID) : [Tokens.ID, State.COMMAIDLIST2],
            
            # commaidlist2 state
            (State.COMMAIDLIST2, Tokens.COMMA) : [Tokens.COMMA, Tokens.ID, State.COMMAIDLIST2],
            (State.COMMAIDLIST2, Tokens.RPARENTH) : [],
            
            # idlist state
            (State.IDLIST, Tokens.LBRACKET) : [Tokens.LBRACKET, State.IDLIST1, Tokens.RBRACKET],
            
            # idlist1 state
            (State.IDLIST1, Tokens.ID) : [Tokens.ID, State.IDLIST1],
            (State.IDLIST1, Tokens.RBRACKET) : [],
            
            # rule state
            (State.RULE, Tokens.ID) : [State.ARG, State.RULE1],
            (State.RULE, Tokens.UNDERSCORE) : [State.ARG, State.RULE1],
            (State.RULE, Tokens.ASTERISK) : [State.ARG, State.RULE1],
            (State.RULE, Tokens.LBRACKET) : [State.ARG, State.RULE1],
            (State.RULE, Tokens.DOLLAR) : [State.ARG, State.RULE1],
            
            # rule1 state
            (State.RULE1, Tokens.ID) : [State.EXPR, Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.UNDERSCORE) : [State.EXPR, Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.DOLLAR) : [State.EXPR, Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.ASTERISK) : [State.EXPR, Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.LBRACKET) : [State.EXPR, Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.BECOMES) : [Tokens.BECOMES, State.EXPR, State.ENVIRON, State.NEGENVIRON, Tokens.SEMICOLON],
            (State.RULE1, Tokens.COLON) : [Tokens.COLON, Tokens.SEMICOLON],
            
            # expr state
            (State.EXPR, Tokens.ID) : [State.ARG, State.EXPR1],
            (State.EXPR, Tokens.UNDERSCORE) : [State.ARG, State.EXPR1],
            (State.EXPR, Tokens.ASTERISK) : [State.ARG, State.EXPR1],
            (State.EXPR, Tokens.LBRACKET) : [State.ARG, State.EXPR1],
            (State.EXPR, Tokens.DOLLAR) : [State.ARG, State.EXPR1],
            
            # expr1 state
            (State.EXPR1, Tokens.ID) : [State.ARG, State.EXPR1],
            (State.EXPR1, Tokens.UNDERSCORE) : [State.ARG, State.EXPR1],
            (State.EXPR1, Tokens.ASTERISK) : [State.ARG, State.EXPR1],
            (State.EXPR1, Tokens.LBRACKET) : [State.ARG, State.EXPR1],
            (State.EXPR1, Tokens.DOLLAR) : [State.ARG, State.EXPR1],
            (State.EXPR1, Tokens.BECOMES) : [],
            (State.EXPR1, Tokens.STRIKE) : [],
            (State.EXPR1, Tokens.DSTRIKE) : [],
            (State.EXPR1, Tokens.SEMICOLON) : [],
            
            # arg state
            (State.ARG, Tokens.ID) : [Tokens.ID],
            (State.ARG, Tokens.UNDERSCORE) : [Tokens.UNDERSCORE],
            (State.ARG, Tokens.ASTERISK) : [Tokens.ASTERISK],
            (State.ARG, Tokens.DOLLAR) : [Tokens.DOLLAR],
            (State.ARG, Tokens.LBRACKET) : [State.IDLIST],
            
            # environ state
            (State.ENVIRON, Tokens.STRIKE) : [Tokens.STRIKE, State.EXPR],
            (State.ENVIRON, Tokens.DSTRIKE) : [],
            (State.ENVIRON, Tokens.SEMICOLON) : [],
            
            # negenviron state
            (State.NEGENVIRON, Tokens.DSTRIKE) : [Tokens.DSTRIKE, State.EXPR],
            (State.NEGENVIRON, Tokens.SEMICOLON) : []
        }
    
    def parse(self) -> Folder:
        self.stack.append(Tokens.EOF)
        self.stack.append(State.START)
        a = self.lexer.lex()
        
        self.prime_table()
        
        while len(self.stack) > 0:
            tos = self.stack[len(self.stack) - 1]
            
            if isinstance(tos, Reduce):
                fld = Folder(tos.state, "", self.lexer.lineno)
                for i in range(tos.count):
                    k = self.value_stack.pop()
                    if (k.state == State.FEATURELIST or
                        k.state == State.RULELIST or
                        k.state == State.SYMBOLLIST or
                        k.state == State.IDLIST1 or
                        k.state == State.RULE1 or
                        k.state == State.EXPR1 or
                        k.state == State.COMMAIDLIST1 or
                        k.state == State.COMMAIDLIST2 or
                        k.state == State.ARG):
                        fld.items.extend(k.items)
                    elif (k.state.type() == 'term' and 
                          not k.state == Tokens.ID and
                          not k.state == Tokens.BECOMES and
                          not k.state == Tokens.UNDERSCORE and
                          not k.state == Tokens.ASTERISK and
                          not k.state == Tokens.DOLLAR): 
                        pass
                    else: fld.items.append(k)
                
                if tos.state == State.RULE and len(fld.items) > 2:
                    if len(fld.items) > 5:
                        x = None
                        if fld.items[len(fld.items) -1].state == State.EXPR:
                            x = fld.items[len(fld.items) - 1].items.copy()
                            fld.items.pop()
                            fld.items[len(fld.items) - 1].items.extend(x)
                        else:
                            x = fld.items[len(fld.items) - 1].copy()
                            fld.items.pop()
                            fld.items[len(fld.items) - 1].items.append(x)
                        
                    
                    if not fld.items[len(fld.items) -1].state == State.EXPR:
                        x = fld.items[len(fld.items) - 1].copy()
                        fld.items[len(fld.items) - 1] = Folder(State.EXPR, "", self.lexer.lineno)
                        fld.items[len(fld.items) -1].items.append(x)
                
                self.value_stack.append(fld)
                self.stack.pop()
            
            elif tos.type() == 'non-term':
                if self.table.get((tos, a)) != None:
                    self.stack.pop()
                    self.stack.append(Reduce(tos, len(self.table[(tos, a)])))
                    i = len(self.table[(tos, a)]) - 1
                    while (i >= 0):
                        self.stack.append(self.table[(tos, a)][i])
                        i -= 1
                else: raise Exception(f"parser error: cannot proceed with {tos} state and {a} input at line {self.lexer.lineno}")
            
            elif tos.type() == 'term':
                if tos == a:
                    if tos == Tokens.EOF: return self.value_stack[0]
                    self.value_stack.append(Folder(tos, self.lexer.lexeme, self.lexer.lineno))
                    self.stack.pop()
                    a = self.lexer.lex()
                else: raise Exception(f"error: unexpected terminal\nexpected {tos}, got {a} at line {self.lexer.lineno}")