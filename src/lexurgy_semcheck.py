from lexurgy_parser import Folder, State
from lexurgy_scanner import Tokens
import os
import re
from pathlib import Path

class FeatureItem:
    def __init__(self, feature, value):
        self.feature = feature
        self.value = value
    
    def __str__(self):
        return f'feature: {self.value} of {self.feature}'
        
class SymbolItem:
    def __init__(self, symbol, items: list):
        self.symbol = symbol
        self.items = items
    
    def __str__(self):
        return f'symbol: {self.symbol}, items: {self.items}'
        
class RuleItem:
    def __init__(self, ifstmt, thenstmt, cond, negcond):
        self.ifstmt = ifstmt
        self.thenstmt = thenstmt
        self.cond = cond
        self.negcond = negcond
        
    def __str__(self):
        return f'if: {self.ifstmt} then: {self.thenstmt} where: {self.cond} except: {self.negcond}'
    
class Checker:
    def __init__(self, res_file_dir:str, fld:Folder):
        self.file = res_file_dir
        file = open(res_file_dir, 'r')
        self.words = file.read().split("\n")
        file.close()
        
        if not os.path.isdir('results'):
            mydir = 'results'
            parent_dir = os.getcwd()
            path = os.path.join(parent_dir, mydir)
            os.mkdir(path)
        
        self.output_dir = './results/results.mylexres'
        self.output_buffer : list[str] = []
        
        """ i = 0
        while True:
            name = f'./results/res{i}.txt'
            if not os.path.exists(name):
                self.output_dir = name
                self.output_buffer:list[str] = []
                break;
            i += 1 """
        
        self.feats = {}
        self.symbs = {}
        self.rules = []
        self.root = fld
        
        self.init()

    def find_feat(self, feat: str, lst: list):
        for i in lst:
            if isinstance(i, FeatureItem):
                if i.value == feat: return True
        return False

    def convert_symbol_by_feature(self, newfeats:list, symb:str):
        oldfeats = self.symbs[symb].copy()
        for i in newfeats:
            samefeat = [x for x in oldfeats if not x[0] == '*' and sorted(self.feats[i]) == sorted(self.feats[x])]
            if len(samefeat) == 0:
                oldfeats.append(i)
            else:
                oldfeats.remove(samefeat[0])
                oldfeats.append(i)
        oldfeats.sort()
        if oldfeats not in self.symbs.values():
            raise Exception(f'no symbol attached to features {oldfeats}')
        else: return [k for k, v in self.symbs.items() if v == oldfeats][0]
        

    def get_symbols_by_features(self, featlist:list):
        tmp = self.symbs.copy()
        for i in featlist:
            tmp = dict([(k, v) for k, v in tmp.items() if i in tmp[k]])
        return [k for k in tmp]
    
    def write_line(self, line:str):
        self.output_buffer.append(line + '\n')
        
    def close_output(self):
        file = open(self.output_dir, 'w')
        file.writelines(self.output_buffer)
        file.close()
        print(f"generated output at {self.output_dir}")
        

    def semcheck(self):
        # get items and rules
        
        # might have to implement this iteratively, by myself
        # so, you loop through the string until you find a passable example of the symbol
        # if you find one, store symbol index, test if all the proceeding symbols could possibly be it
        # probably best implemented with a state diagram, to be honest. A state diagram that takes the thing as input
        for i in [x for x in self.rules if not isinstance(x, str)]:
            org, fin, pcon, ncon = i
            regex_org = ''
            for k in org:
                # for feature lists
                if isinstance(k, list):
                    lst = ''.join(self.get_symbols_by_features(k))
                    regex_org += f'([{lst}])'
                else:
                    if k == '*':
                        regex_org += f'()'
                    elif k == '$':
                        if org.index(k) == 0:
                            regex_org += '^'
                        elif org.index(k) == len(org)-1:
                            regex_org += '$'
                        else: raise Exception("dollar sign must appear either at the beginning or the end")
                    else: regex_org += f'({k})'
                    
            def zikr():
                i = 2
                    
            lookbh_pos = ''
            lookbh_neg = ''
            lookhd_pos = ''
            lookhd_neg = ''
            for k in [pcon, ncon]:
                x = ''
                in_lookbehind = False
                for m in k:
                    if isinstance(m, list):
                        lst = ''.join(self.get_symbols_by_features(m))
                        x += f'[{lst}]'
                    else:
                        if m == '_':
                            if k == pcon: lookbh_pos = x
                            else: lookbh_neg = x
                            in_lookbehind = True
                            x = ''
                        elif m == '$':
                            if k.index(m) == len(k)-1:
                                x += '$'
                            else: x += '^'
                        else: x += k
                if k == pcon:
                    lookhd_pos = x
                else: lookhd_neg = x
            
            def get_repl(match):
                res = ''
                for i in range(len(fin)):
                    s = ''
                    if isinstance(fin[i], list):
                        s = self.convert_symbol_by_feature(fin[i], match.group(i+1))
                    else:
                        if fin[i] == '*':
                            pass
                        else: s = fin[i]
                    res += s if s != '' else ''
                return res
            
            def patt_eq(mat1, patt2, word):
                id1 = (mat1.group(), mat1.start(), mat1.end())
                mat2 = []
                for i in patt2.finditer(word):
                    mat2.append((i.group(), i.start(), i.end()))
                return id1 in mat2
                    
            for k in self.words:
                res = k
                pattern = re.compile(f'(?<={lookbh_pos}){regex_org}(?={lookhd_pos})')
                negpattern = re.compile('' if (lookbh_neg == '' and lookhd_neg == '') else f'(?<={lookbh_neg}){regex_org}(?={lookhd_neg})')
                for match in pattern.finditer(k):
                    if not patt_eq(match, negpattern, k):
                        res = pattern.sub(get_repl, k)
                self.write_line(res)
            self.close_output()
        
    def init(self):
        m = len(self.root.items) - 1
        while m >= 0:
            x = self.root.items[m]
            match x.state:
                case State.FEATURE:
                    for i in x.items[0].items:
                        if i.lexeme in self.feats:
                            raise Exception(f'duplicate feature value \"{i.lexeme}\" found at line {i.lineno}')
                        self.feats[i.lexeme] = x.items[1].lexeme
                
                case State.SYMBOL:
                    mylist = []
                    if len(x.items[1].lexeme) > 1:
                        raise Exception(f'symbol "{x.items[1].lexeme}" must be a char on line {x.items[1].lineno}')
                    
                    for i in x.items[0].items:
                        if self.feats.get(i.lexeme) == None:
                            raise Exception(f'feature \"{i.lexeme}\" does not exist on line {i.lineno}')
                        if len([v for v in mylist if self.feats[v] == self.feats[i.lexeme]]) > 0:
                            raise Exception(f'cannot have items from the same feature in a symbol definiton on line {i.lineno}')
                        mylist.append(i.lexeme)

                    tmp = []
                    for i in self.feats:
                        res = "*" + self.feats[i]
                        if len([v for v in mylist if self.feats[v] == self.feats[i]]) == 0 and res not in tmp:
                            tmp.append(res)
                    mylist.extend(tmp)
                    
                    if x.items[1].lexeme in self.symbs:
                        raise Exception(f'symbol \"{x.items[1].lexeme}\" on line {x.items[1].lineno} already defined')
                    if mylist in self.symbs.values():
                        valres = [k for k, v in self.symbs.items() if v == mylist]
                        raise Exception(f'symbol definition for \"{x.items[1].lexeme}\" already used for symbol \"{valres[0]}\" earlier')
                    
                    self.symbs[x.items[1].lexeme] = sorted(mylist)
                
                case State.RULE:
                    iflist = []
                    thenlist = []
                    condlist = []
                    negcondlist = []
                    lstlist = [negcondlist, condlist, thenlist, [], iflist]
                    
                    if (len(x.items) >= 5):
                        if (len([f.state for f in x.items[4].items if f.state == Tokens.DOLLAR]) > 0 or
                            len([f.state for f in x.items[2].items if f.state == Tokens.DOLLAR]) > 0):
                            raise Exception(f"dollar sign token only permissible in environment specifiers at line {x.lineno}")
                        if len(x.items[0].items) > 0:
                            if len([f.state for f in x.items[0].items[0].items if f.state == Tokens.ASTERISK]) > 0:
                                raise Exception(f"asterisk sign cannot appear in exception environment at line {x.lineno}")
                            tmp = [f.state for f in x.items[0].items[0].items if f.state == Tokens.UNDERSCORE]
                            if len(tmp) < 1:
                                raise Exception(f"underscore missing in exception environment at line {x.lineno}")
                            elif len(tmp) > 1:
                                raise Exception(f"too many underscores in exception environment at line {x.lineno}")
                        if len(x.items[1].items) > 0:
                            if len([f.state for f in x.items[1].items[0].items if f.state == Tokens.ASTERISK]) > 0:
                                raise Exception(f"asterisk sign token cannot appear in environment {x.lineno}")
                            tmp = [f.state for f in x.items[1].items[0].items if f.state == Tokens.UNDERSCORE]
                            if len(tmp) < 1:
                                raise Exception(f"underscore missing in environment at line {x.lineno}")
                            elif len(tmp) > 1:
                                raise Exception(f"too many underscores in environment at line {x.lineno}")
                        for i in range(len(x.items)):
                            if i == 3: continue
                            if i == 4 or i == 2:
                                q = x.items[i].items
                            else: 
                                if len(x.items[i].items) > 0:
                                    q = x.items[i].items[0].items
                                else: q = []
                            s = len(q) - 1
                            while s >= 0:
                                j = q[s]
                                if j.state == State.IDLIST:
                                    temp = []
                                    k = len(j.items) - 1
                                    while k >= 0:
                                        if j.items[k].lexeme not in self.feats:
                                            raise Exception(f'feature \"{j.items[k].lexeme}\" does not exist')
                                        temp.append(j.items[k].lexeme)
                                        k -= 1
                                    lstlist[i].append(temp)
                                else:
                                    lstlist[i].append(j.lexeme)
                                s -= 1
                                
                        if not len(lstlist[4]) == len(lstlist[2]):
                            raise Exception(f'lhs and rhs of rule at line {x.lineno} must be of the same length')
                        self.rules.append((lstlist[4], lstlist[2], lstlist[1], lstlist[0]))
                    else:
                        self.rules.append(x.items[0].lexeme)
            m -= 1