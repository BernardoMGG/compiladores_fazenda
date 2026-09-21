# 🌾 MineC — Linguagem de Programação para uma Fazenda Automática

Projeto da disciplina **Linguagens Formais e Compiladores**. MineC é uma linguagem imperativa, pequena e de leitura fácil, com vocabulário inspirado no Minecraft, usada para descrever o comportamento de uma fazenda automática simulada: ler sensores (umidade, temperatura), tomar decisões com condições e laços e acionar atuadores (bomba de água, ventilador).

Escopo desta entrega: **definição da linguagem, análise léxica e análise sintática** (implementadas em Python).

## Sumário

- [Exemplo rápido](#exemplo-rápido)
- [A linguagem em resumo](#a-linguagem-em-resumo)
- [Como executar](#como-executar)
- [Estrutura do repositório](#estrutura-do-repositório)
- [Como o compilador funciona](#como-o-compilador-funciona)
- [Verificação da gramática](#verificação-da-gramática)
- [Documentação](#documentação)

## Exemplo rápido

```minec
# Irrigação automática por umidade do solo
observer umidade = 34
lever bomba = 8
craft limite = 30

mine umidade
if umidade < limite {
    say "Solo seco: ligando a bomba"
    power bomba
    wait 10
    unpower bomba
} else {
    say "Solo úmido: nada a fazer"
}
```

## A linguagem em resumo

| Conceito | Palavra MineC | Ideia no Minecraft |
|---|---|---|
| Variável | `craft` | fabricar algo |
| Sensor | `observer` | bloco Observer |
| Atuador | `lever` | alavanca |
| Ler sensor | `mine` | minerar um dado |
| Ligar / desligar atuador | `power` / `unpower` | energizar redstone |
| Função | `command` | bloco de comando |
| Retorno | `drop` | item dropado |
| Saída | `say` | chat |
| Espera (segundos) | `wait` | — |

Além disso:

- **Controle de fluxo:** `if` / `else if` / `else`, `while` e `repeat N`.
- **Expressões:** aritméticas (`+ - * /`), relacionais (`< > <= >= == !=`) e lógicas (`and`, `or`, `not`), com parênteses e precedência definida.
- **Tipos:** inteiro, decimal, texto e booleano (`true` / `false`), verificados numa fase semântica futura.
- **Funções:** `command` só no nível global, com parâmetros e retorno via `drop`.
- **Sem `;`:** blocos com chaves `{ }`; espaços e quebras de linha só separam tokens.
- **Comentários** de linha com `#`.
- **Sensível a maiúsculas:** `Craft` não é `craft`.

## Como executar

Requer apenas **Python 3.9+** (sem dependências externas).

```bash
# Demonstração: tabela de tokens, AST e exemplos de erros léxicos/sintáticos
python exemplo_minec.py

# Valida a gramática (LL(1)) e os arquivos de exemplos/
python ferramentas/validador_gramatica.py

# Imprime os conjuntos FIRST/FOLLOW de cada não terminal
python ferramentas/validador_gramatica.py sets
```

Para usar o compilador em código próprio:

```python
from minec import LexerMineC, ParserMineC

tokens = LexerMineC(codigo_fonte).tokenize()
ast = ParserMineC(tokens).parse()
print(ast.print_tree())
```

## Estrutura do repositório

```
.
├── minec.py                      # Lexer, nós da AST e Parser (descida recursiva)
├── exemplo_minec.py              # Demonstração completa (tokens, AST e erros)
├── exemplos/
│   ├── 01_horta_basica.minec     # Variáveis, say, repeat e wait
│   ├── 02_irrigacao.minec        # Sensor, atuador e if/else
│   └── 03_fazenda_completa.minec # command, drop, while, else if, expressões
├── ferramentas/
│   └── validador_gramatica.py    # FIRST/FOLLOW, tabela LL(1) e parser preditivo
└── docs/
    ├── documentacao.md           # Especificação léxica e sintática completa
    └── tabela-de-tokens.md       # Todos os tokens da linguagem
```

## Como o compilador funciona

```
código-fonte  →  Analisador léxico  →  tokens  →  Analisador sintático  →  AST
   (.minec)        (LexerMineC)                      (ParserMineC)
```

1. **Análise léxica** (`LexerMineC`): varre o texto caractere a caractere, com controle de linha e coluna, e produz a lista de tokens terminada em `TK_EOF`. Reconhece 39 tokens (palavras reservadas, booleanos, identificador, literais inteiro/decimal/texto, operadores e delimitadores). Segue a regra do maior casamento (`<=` antes de `<`) e descarta espaços e comentários.
2. **Análise sintática** (`ParserMineC`): parser de **descida recursiva**, com uma função por regra da gramática. As expressões seguem uma cascata de precedência, da mais fraca para a mais forte: `or` → `and` → `== !=` → `< > <= >=` → `+ -` → `* /` → `not` e `-` unários.
3. **AST:** cada construção da linguagem (declaração, atribuição, chamada, `if`, `while`, `repeat`, operações etc.) é um nó, e `print_tree()` desenha a árvore no terminal.
4. **Erros:** erros léxicos e sintáticos informam linha, coluna e o trecho próximo ao problema, por exemplo `[Análise Sintática Error] Linha 3, Coluna 5 perto de '}': ...`.

## Verificação da gramática

O script [`ferramentas/validador_gramatica.py`](ferramentas/validador_gramatica.py) confere que a gramática e os exemplos são consistentes:

1. implementa o scanner descrito na documentação;
2. calcula automaticamente **FIRST/FOLLOW** e a **tabela LL(1)**, detectando conflitos;
3. executa um parser preditivo sobre os arquivos de `exemplos/` e sobre casos de erro.

Resultado atual: **nenhum conflito LL(1)** e os três exemplos são aceitos.

## Documentação

- [`docs/documentacao.md`](docs/documentacao.md): visão geral, expressões regulares e AFD do léxico, gramática BNF, precedência, FIRST/FOLLOW, verificação LL(1), exemplo de derivação, erros e regras semânticas informais.
- [`docs/tabela-de-tokens.md`](docs/tabela-de-tokens.md): tabela completa dos tokens, com lexema, significado, exemplo e justificativa das adições feitas à lista original.

## Fora do escopo

Análise semântica (declaração antes do uso, tipos, escopo) e geração de código estão descritas como regras informais na documentação, mas ainda não foram implementadas.
