# 🌾 MineC — Linguagem de Programação para uma Plantação Automática

Projeto da disciplina **Linguagens Formais e Compiladores**. MineC é uma linguagem imperativa, pequena e de leitura fácil, com vocabulário inspirado no Minecraft, usada para descrever o comportamento de uma plantação automática simulada: **checar a umidade da terra, regar se precisar e observar se a planta já pode ser colhida**.

Na prática, um programa MineC lê sensores (umidade, maturidade), decide com condições e laços e aciona um atuador (a bomba de água). A colheita **não é automática**: o programa apenas observa e avisa quando a planta está pronta.

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
# Um ciclo: checa a umidade, rega se precisar e observa a maturidade
observer umidade = 34
observer maturidade = 92
lever bomba = 8
craft limiteSeco = 30
craft limiteMaduro = 90

mine umidade
if umidade < limiteSeco {
    say "Solo seco: ligando a bomba"
    power bomba
    wait 10
    unpower bomba
}

mine maturidade
if maturidade >= limiteMaduro {
    say "Pronta para colher"
} else {
    say "Ainda crescendo"
}
```

O ciclo completo, em laço e com funções, está em [`exemplos/03_fazenda_completa.minec`](exemplos/03_fazenda_completa.minec).

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

### Pré-requisitos

- **Python 3.9 ou superior** (sem dependências externas, não precisa de `pip install`).
- Para conferir a versão instalada: `python --version`.

### Passo a passo

1. Abra um terminal **na pasta do projeto** (a que contém `minec.py`). No VS Code: *Terminal → New Terminal*.
2. Rode um dos comandos abaixo.

```bash
# Demonstração completa: tabela de tokens, AST e exemplos de erros léxicos/sintáticos
python exemplo_minec.py

# Valida a gramática (sem conflitos LL(1)) e os arquivos de exemplos/
python ferramentas/validador_gramatica.py

# Imprime os conjuntos FIRST/FOLLOW de cada não terminal
python ferramentas/validador_gramatica.py sets
```

> **Windows:** se `python` não for reconhecido, use `py` no lugar (ex.: `py exemplo_minec.py`).
> **Emojis ou acentos quebrados:** no PowerShell, rode antes `$env:PYTHONIOENCODING = "utf-8"`.

O `exemplo_minec.py` executa o programa MineC que está escrito dentro dele (a fazenda completa). Ele mostra, em ordem, o código-fonte, a tabela de tokens, a AST e cinco exemplos de erros.

### Rodar um arquivo `.minec`

Para analisar qualquer arquivo de `exemplos/` (ou o seu), mostrando a AST:

```bash
python -c "from minec import *; print(ParserMineC(LexerMineC(open('exemplos/02_irrigacao.minec', encoding='utf-8').read()).tokenize()).parse().print_tree())"
```

Troque `02_irrigacao.minec` pelo arquivo desejado. Se o código tiver erro léxico ou sintático, a mensagem mostra linha e coluna.

### Usar como biblioteca

```python
from minec import LexerMineC, ParserMineC

codigo_fonte = 'craft x = 1 + 2\nsay x'

tokens = LexerMineC(codigo_fonte).tokenize()   # lista de tokens (termina em TK_EOF)
ast = ParserMineC(tokens).parse()               # árvore sintática
print(ast.print_tree())
```

## Estrutura do repositório

```
.
├── minec.py                      # Lexer, nós da AST e Parser (descida recursiva)
├── exemplo_minec.py              # Demonstração completa (tokens, AST e erros)
├── exemplos/
│   ├── 01_horta_basica.minec     # Variáveis, say, repeat e wait
│   ├── 02_irrigacao.minec        # Checa a umidade e rega (sensor, atuador, if/else)
│   └── 03_fazenda_completa.minec # Ciclo completo: umidade, rega e observação da maturidade
│                                 # (command, drop, while, else if, expressões)
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
