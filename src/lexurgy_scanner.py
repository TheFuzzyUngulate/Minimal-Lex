from enum import Enum, auto

class Tokens(Enum):
    EOF = auto()
    SEMICOLON = auto()
    COLON = auto()
    UNDERSCORE = auto()
    ASTERISK = auto()
    STRIKE = auto()
    DSTRIKE = auto()
    LPARENTH = auto()
    RPARENTH = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    BECOMES = auto()
    DOLLAR = auto()
    SYMBOL = auto()
    FEATURE = auto()
    ID = auto()
    
    def __str__(self):
        return self.name
    
    def type(self):
        return 'term'

class Lexer:
    def __init__(self, filedir):
        # add filename and buffer
        self.file = filedir
        file = open(filedir, 'rb')
        self.buffer = file.read() + bytes(1)
        file.close()
        
        # important elements
        self.lexeme = ""
        self.lineno = 1
        self.next_char = 0
        
        # unlex buffer
        self.unlex_buf = []
        
        # states
        self.in_comment = False
        self.ending_semicolon = False
        
    def unlex(self, lexed):
        self.unlex_buf.append(lexed)
    
    def lex(self):
        if len(self.unlex_buf) > 0:
            return self.unlex_buf.pop()
        
        while True:
            # read character
            char = self.buffer[self.next_char]
            self.next_char += 1
            self.lexeme = ""
            
            # ignore spaces
            while char and chr(char).isspace() and char != 10:
                char = self.buffer[self.next_char]
                self.next_char += 1
            
            # else, match
            match char:
                # EOF
                case 0:
                    if not self.in_comment and not self.ending_semicolon:
                        self.next_char -= 1
                        self.ending_semicolon = True
                        return Tokens.SEMICOLON
                    else: return Tokens.EOF
                # newline
                case 10:
                    self.lineno += 1
                    self.line_tok_count = 0
                    if not self.in_comment:
                        while True:
                            k = self.lex()
                            if k != Tokens.SEMICOLON: break
                        self.unlex(k)
                        return Tokens.SEMICOLON
                    self.in_comment = False
                # "#" comment delimiter
                case 35:
                    self.in_comment = True
                    while char and char != 10:
                        char = self.buffer[self.next_char]
                        self.next_char += 1
                    self.next_char -= 1
                # "=>" operation
                case 61:
                    char = self.buffer[self.next_char]
                    self.next_char += 1
                    if (char == 62): return Tokens.BECOMES
                    else:
                        raise Exception(f'Invalid lexeme {"=" + chr(char)} at {self.lineno}')
                case 58:
                    return Tokens.COLON
                case 36:
                    self.lexeme = "$"
                    return Tokens.DOLLAR
                case 95:
                    self.lexeme = "_"
                    return Tokens.UNDERSCORE
                case 42:
                    self.lexeme = "*"
                    return Tokens.ASTERISK
                case 47:
                    char = self.buffer[self.next_char]
                    self.next_char += 1
                    if (char == 47): return Tokens.DSTRIKE
                    else:
                        self.next_char -= 1
                        return Tokens.STRIKE
                case 40:
                    return Tokens.LPARENTH
                case 41:
                    return Tokens.RPARENTH
                case 91:
                    return Tokens.LBRACKET
                case 93:
                    return Tokens.RBRACKET
                case 44:
                    return Tokens.COMMA
                case _:
                    # "-" is 45
                    if (chr(char).isalpha()):
                        while True:
                            self.lexeme = self.lexeme + chr(char)
                            char = self.buffer[self.next_char]
                            self.next_char += 1
                            if (chr(char).isalpha() == False and 
                                chr(char).isnumeric() == False and
                                char != 45):
                                break
                        self.next_char -= 1
                        if self.lexeme.lower() == 'feature':
                            return Tokens.FEATURE
                        elif self.lexeme.lower() == 'symbol':
                            return Tokens.SYMBOL
                        else: return Tokens.ID
                    else: raise Exception(f'Invalid identifier \"{self.lexeme}\" at {self.lineno}')
        