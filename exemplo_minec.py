import sys
from minec import LexerMineC, ParserMineC

sys.stdout.reconfigure(encoding="utf-8")

# =====================================================================
# CÓDIGO FONTE EM MINEC PARA TESTAR
# =====================================================================

minec_code = """
# Fazenda automática de trigo - MineC

observer umidade = 34
observer temperatura = 35
lever bomba = 8
lever ventilador = 9

craft limiteSeco = 30
craft limiteQuente = 32.5
craft ciclos = 0

command irrigar(segundos) {
    say "Irrigando..."
    power bomba
    wait segundos
    unpower bomba
}

command mediaSimples(a, b) {
    drop (a + b) / 2
}

say "Fazenda iniciada"

craft anterior = 0

while true {
    mine umidade
    mine temperatura

    craft media = mediaSimples(umidade, anterior)
    anterior = umidade

    if media < limiteSeco and not (temperatura > limiteQuente) {
        irrigar(10)
        ciclos = ciclos + 1
    } else if temperatura >= limiteQuente {
        power ventilador
    } else {
        unpower ventilador
    }

    if ciclos == 5 {
        say "Ciclo de manutenção"
        ciclos = 0
    }

    wait 60
}
"""

print("=====================================================================")
print("🌾 CÓDIGO FONTE MINEC ENVIADO AO COMPILADOR")
print("=====================================================================")
print(minec_code)

# 1. EXECUÇÃO DA ANÁLISE LÉXICA
lexer = LexerMineC(minec_code)
tokens = lexer.tokenize()

print("\n=====================================================================")
print("⛏️ RESULTADO DA ANÁLISE LÉXICA (TABELA DE TOKENS)")
print("=====================================================================")
for t in tokens:
    print(t)

# 2. EXECUÇÃO DA ANÁLISE SINTÁTICA
parser = ParserMineC(tokens)
ast = parser.parse()

print("\n=====================================================================")
print("🌳 RESULTADO DA ANÁLISE SINTÁTICA (ÁRVORE DE SINTAXE ABSTRATA - AST)")
print("=====================================================================")
print(ast.print_tree())

# 3. EXEMPLOS DE ERROS (léxico e sintático)
print("=====================================================================")
print("💥 EXEMPLOS DE ERROS DETECTADOS")
print("=====================================================================")

codigos_com_erro = {
    "Erro léxico (caractere inválido)": 'craft x = 3 @ 2',
    "Erro léxico (string não fechada)": 'say "Olá',
    "Erro sintático (falta '=')": 'craft limite 30',
    "Erro sintático (bloco não fechado)": 'if x < 3 {\n    say "a"\n',
    "Erro sintático (command dentro de bloco)": 'while true {\n    command f() { }\n}',
}

for titulo, codigo in codigos_com_erro.items():
    print(f"\n>> {titulo}\n{codigo}")
    try:
        ParserMineC(LexerMineC(codigo).tokenize()).parse()
    except SyntaxError as e:
        print(e)
