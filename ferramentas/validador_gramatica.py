import re, sys, glob, json

RESERVED = {
 'craft':'TK_CRAFT','mine':'TK_MINE','say':'TK_SAY','if':'TK_IF','else':'TK_ELSE','while':'TK_WHILE',
 'repeat':'TK_REPEAT','power':'TK_POWER','unpower':'TK_UNPOWER','wait':'TK_WAIT','observer':'TK_OBSERVER',
 'lever':'TK_LEVER','command':'TK_COMMAND','drop':'TK_DROP','true':'TK_TRUE','false':'TK_FALSE',
 'and':'TK_AND','or':'TK_OR','not':'TK_NOT'}
SINGLE = {'+':'TK_PLUS','-':'TK_MINUS','*':'TK_STAR','/':'TK_SLASH','(':'TK_LPAREN',')':'TK_RPAREN',
          '{':'TK_LBRACE','}':'TK_RBRACE',',':'TK_COMMA'}

class LexError(Exception): pass

def lex(src):
    toks=[]; i=0; line=1; n=len(src)
    while i<n:
        c=src[i]
        if c=='\n': line+=1; i+=1; continue
        if c in ' \t\r': i+=1; continue
        if c=='#':
            while i<n and src[i]!='\n': i+=1
            continue
        if c.isascii() and (c.isalpha() or c=='_'):
            j=i
            while j<n and src[j].isascii() and (src[j].isalnum() or src[j]=='_'): j+=1
            lx=src[i:j]; toks.append((RESERVED.get(lx,'TK_IDENTIFIER'),lx,line)); i=j; continue
        if c.isdigit() and c.isascii():
            j=i
            while j<n and src[j].isdigit(): j+=1
            if j<n and src[j]=='.':
                k=j+1
                if k<n and src[k].isdigit():
                    while k<n and src[k].isdigit(): k+=1
                    toks.append(('TK_DECIMAL',src[i:k],line)); i=k; continue
                raise LexError(f'linha {line}: decimal malformado')
            toks.append(('TK_INTEGER',src[i:j],line)); i=j; continue
        if c=='"':
            j=i+1
            while j<n and src[j] not in '"\n': j+=1
            if j>=n or src[j]=='\n': raise LexError(f'linha {line}: string nao fechada')
            toks.append(('TK_STRING',src[i:j+1],line)); i=j+1; continue
        two=src[i:i+2]
        if two=='==': toks.append(('TK_EQUAL',two,line)); i+=2; continue
        if two=='!=': toks.append(('TK_NOT_EQUAL',two,line)); i+=2; continue
        if two=='<=': toks.append(('TK_LESS_EQUAL',two,line)); i+=2; continue
        if two=='>=': toks.append(('TK_GREATER_EQUAL',two,line)); i+=2; continue
        if c=='=': toks.append(('TK_ASSIGN',c,line)); i+=1; continue
        if c=='<': toks.append(('TK_LESS',c,line)); i+=1; continue
        if c=='>': toks.append(('TK_GREATER',c,line)); i+=1; continue
        if c in SINGLE: toks.append((SINGLE[c],c,line)); i+=1; continue
        raise LexError(f'linha {line}: caractere invalido {c!r}')
    toks.append(('TK_EOF','',line))
    return toks

# Gramatica (BNF pura). Nao-terminais = chaves; terminais = TK_*; 'eps' = vazio
G = {
 'Programa':[['ListaItens']],
 'ListaItens':[['Item','ListaItens'],[]],
 'Item':[['Comando'],['Instrucao']],
 'Comando':[['TK_COMMAND','TK_IDENTIFIER','TK_LPAREN','Params','TK_RPAREN','Bloco']],
 'Params':[['TK_IDENTIFIER','ParamsR'],[]],
 'ParamsR':[['TK_COMMA','TK_IDENTIFIER','ParamsR'],[]],
 'Bloco':[['TK_LBRACE','ListaInstr','TK_RBRACE']],
 'ListaInstr':[['Instrucao','ListaInstr'],[]],
 'Instrucao':[['DeclVar'],['DeclSensor'],['DeclAtuador'],['InstrId'],['Leitura'],['Saida'],['Condicional'],
              ['Enquanto'],['Repita'],['Liga'],['Desliga'],['Espera'],['Retorno']],
 'DeclVar':[['TK_CRAFT','TK_IDENTIFIER','TK_ASSIGN','Expr']],
 'DeclSensor':[['TK_OBSERVER','TK_IDENTIFIER','TK_ASSIGN','Expr']],
 'DeclAtuador':[['TK_LEVER','TK_IDENTIFIER','TK_ASSIGN','Expr']],
 'InstrId':[['TK_IDENTIFIER','InstrIdR']],
 'InstrIdR':[['TK_ASSIGN','Expr'],['TK_LPAREN','Args','TK_RPAREN']],
 'Leitura':[['TK_MINE','TK_IDENTIFIER']],
 'Saida':[['TK_SAY','Expr']],
 'Condicional':[['TK_IF','Expr','Bloco','Senao']],
 'Senao':[['TK_ELSE','SenaoCorpo'],[]],
 'SenaoCorpo':[['Condicional'],['Bloco']],
 'Enquanto':[['TK_WHILE','Expr','Bloco']],
 'Repita':[['TK_REPEAT','Expr','Bloco']],
 'Liga':[['TK_POWER','TK_IDENTIFIER']],
 'Desliga':[['TK_UNPOWER','TK_IDENTIFIER']],
 'Espera':[['TK_WAIT','Expr']],
 'Retorno':[['TK_DROP','Expr']],
 'Args':[['Expr','ArgsR'],[]],
 'ArgsR':[['TK_COMMA','Expr','ArgsR'],[]],
 'Expr':[['Conj','ExprR']],
 'ExprR':[['TK_OR','Conj','ExprR'],[]],
 'Conj':[['Igual','ConjR']],
 'ConjR':[['TK_AND','Igual','ConjR'],[]],
 'Igual':[['Rel','IgualR']],
 'IgualR':[['OpIgual','Rel','IgualR'],[]],
 'OpIgual':[['TK_EQUAL'],['TK_NOT_EQUAL']],
 'Rel':[['Soma','RelR']],
 'RelR':[['OpRel','Soma','RelR'],[]],
 'OpRel':[['TK_LESS'],['TK_GREATER'],['TK_LESS_EQUAL'],['TK_GREATER_EQUAL']],
 'Soma':[['Termo','SomaR']],
 'SomaR':[['OpSoma','Termo','SomaR'],[]],
 'OpSoma':[['TK_PLUS'],['TK_MINUS']],
 'Termo':[['Unario','TermoR']],
 'TermoR':[['OpMul','Unario','TermoR'],[]],
 'OpMul':[['TK_STAR'],['TK_SLASH']],
 'Unario':[['TK_NOT','Unario'],['TK_MINUS','Unario'],['Primario']],
 'Primario':[['TK_INTEGER'],['TK_DECIMAL'],['TK_STRING'],['TK_TRUE'],['TK_FALSE'],
             ['TK_IDENTIFIER','ChamadaOpc'],['TK_LPAREN','Expr','TK_RPAREN']],
 'ChamadaOpc':[['TK_LPAREN','Args','TK_RPAREN'],[]],
}
START='Programa'; EOF='TK_EOF'

def first_follow():
    nullable=set(); FIRST={A:set() for A in G}
    ch=True
    while ch:
        ch=False
        for A,ps in G.items():
            for p in ps:
                if all(s in nullable for s in p if s in G) and all(s in G for s in p):
                    if A not in nullable: nullable.add(A); ch=True
                for s in p:
                    add = FIRST[s] if s in G else {s}
                    if not add<=FIRST[A]: FIRST[A]|=add; ch=True
                    if s not in nullable: break
    def first_seq(seq):
        r=set()
        for s in seq:
            r|= FIRST[s] if s in G else {s}
            if s not in nullable: return r,False
        return r,True
    FOLLOW={A:set() for A in G}; FOLLOW[START].add(EOF)
    ch=True
    while ch:
        ch=False
        for A,ps in G.items():
            for p in ps:
                for i,s in enumerate(p):
                    if s in G:
                        f,nl=first_seq(p[i+1:])
                        add=f|(FOLLOW[A] if nl else set())
                        if not add<=FOLLOW[s]: FOLLOW[s]|=add; ch=True
    return nullable,FIRST,FOLLOW,first_seq

nullable,FIRST,FOLLOW,first_seq=first_follow()

def build_table():
    T={}; conflicts=[]
    for A,ps in G.items():
        for k,p in enumerate(ps):
            f,nl=first_seq(p)
            look=f|(FOLLOW[A] if nl else set())
            for t in look:
                if (A,t) in T: conflicts.append((A,t,T[(A,t)],k))
                T[(A,t)]=k
    return T,conflicts

TABLE,CONFLICTS=build_table()

def parse(toks):
    stack=[EOF,START]; i=0
    while stack:
        top=stack.pop(); tk=toks[i][0]
        if top in G:
            k=TABLE.get((top,tk))
            if k is None: raise SyntaxError(f'linha {toks[i][2]}: token inesperado {tk} ({toks[i][1]!r}) ao expandir {top}')
            stack.extend(reversed(G[top][k]))
        else:
            if top!=tk: raise SyntaxError(f'linha {toks[i][2]}: esperado {top}, encontrado {tk} ({toks[i][1]!r})')
            i+=1
    return True

def check(src):
    try: parse(lex(src)); return 'OK'
    except (LexError,SyntaxError) as e: return f'ERRO: {e}'

if __name__=='__main__':
    print('conflitos LL(1):',CONFLICTS or 'nenhum')
    print('nao-terminais anulaveis:',sorted(nullable))
    if len(sys.argv)>1 and sys.argv[1]=='sets':
        for A in G:
            print(A,'FIRST=',sorted(FIRST[A]),'FOLLOW=',sorted(FOLLOW[A]))
        sys.exit()
    for f in sorted(glob.glob('exemplos/*.minec')):
        print(f, check(open(f,encoding='utf-8').read()))
    neg={
     'falta chave':'if x < 3 { say "a"',
     'sem expressao no drop':'command f() { drop }',
     'string aberta':'say "abc',
     'caractere invalido':'craft x = 3 @ 2',
     'bang sozinho':'craft x = !3',
     'decimal ruim':'craft x = 3.',
     'craft sem atrib':'craft x',
     'command dentro de bloco':'if true { command f() { } }',
     'ok else if':'if a { } else if b { } else { }',
     'ok chamada instr':'f(1, 2+3)\nx = 4',
     'ok unario':'craft x = -a + -(b*2)\nsay x',
     'ok drop seguido de atrib':'command f(a) { drop a\n x = 3 }',
    }
    for k,v in neg.items(): print(f'{k:28}', check(v))
