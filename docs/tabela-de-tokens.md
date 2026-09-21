# Tabela de Tokens — MineC

MineC é uma linguagem de automação de fazendas no estilo Minecraft, pensada para controlar sensores e atuadores (Arduino e similares).
Esta tabela lista **todos os tokens** reconhecidos pelo analisador léxico. Tokens marcados com ★ foram **adicionados** à lista original da equipe (justificativas na seção 2).

**Total: 39 tokens de linguagem + 1 token auxiliar (`TK_EOF`).**

---

## 1. Tabela

### 1.1 Palavras reservadas (17)

| Token | Lexema | O que representa | Exemplo |
|---|---|---|---|
| `TK_CRAFT` | `craft` | Declara uma variável | `craft limite = 30` |
| `TK_MINE` | `mine` | Lê o valor atual de um sensor | `mine umidade` |
| `TK_SAY` | `say` | Exibe uma saída | `say "Olá"` |
| `TK_IF` | `if` | Condição | `if umidade < 30 { ... }` |
| `TK_ELSE` | `else` | Caso contrário | `else { ... }` |
| `TK_WHILE` | `while` | Repetição com condição | `while true { ... }` |
| `TK_REPEAT` | `repeat` | Repetição determinada (N vezes) | `repeat 5 { ... }` |
| `TK_POWER` | `power` | Liga um atuador | `power bomba` |
| `TK_UNPOWER` | `unpower` | Desliga um atuador | `unpower bomba` |
| `TK_WAIT` | `wait` | Espera (em segundos) | `wait 10` |
| `TK_OBSERVER` | `observer` | Declara um sensor (com o pino) | `observer umidade = 34` |
| `TK_LEVER` ★ | `lever` | Declara um atuador (com o pino) | `lever bomba = 8` |
| `TK_COMMAND` | `command` | Declara uma função | `command irrigar(t) { ... }` |
| `TK_DROP` | `drop` | Retorno de função | `drop valor` |
| `TK_AND` ★ | `and` | E lógico | `a > 1 and b < 2` |
| `TK_OR` ★ | `or` | OU lógico | `a > 1 or b < 2` |
| `TK_NOT` ★ | `not` | Negação lógica | `not bomba` |

### 1.2 Booleanos (2)

| Token | Lexema | O que representa | Exemplo |
|---|---|---|---|
| `TK_TRUE` | `true` | Verdadeiro | `craft ligado = true` |
| `TK_FALSE` | `false` | Falso | `craft ligado = false` |

### 1.3 Identificador (1)

| Token | Lexema (padrão) | O que representa | Exemplo |
|---|---|---|---|
| `TK_IDENTIFIER` | `letra (letra \| dígito)*` | Nome criado pelo programador (variável, sensor, atuador, comando, parâmetro) | `umidade`, `bomba`, `limite_seco` |

### 1.4 Literais (3)

| Token | Lexema (padrão) | O que representa | Exemplo |
|---|---|---|---|
| `TK_INTEGER` | `dígito+` | Número inteiro | `30` |
| `TK_DECIMAL` | `dígito+ . dígito+` | Número decimal | `25.5` |
| `TK_STRING` | `" (qualquer caractere exceto " e quebra de linha)* "` | Texto | `"Horta iniciada"` |

### 1.5 Operadores (11)

| Token | Lexema | O que representa | Exemplo |
|---|---|---|---|
| `TK_ASSIGN` | `=` | Atribuição | `limite = 30` |
| `TK_EQUAL` | `==` | Igualdade | `x == 10` |
| `TK_NOT_EQUAL` ★ | `!=` | Diferença | `x != 10` |
| `TK_LESS` | `<` | Menor que | `umidade < 30` |
| `TK_GREATER` | `>` | Maior que | `temperatura > 35` |
| `TK_LESS_EQUAL` ★ | `<=` | Menor ou igual | `umidade <= 30` |
| `TK_GREATER_EQUAL` ★ | `>=` | Maior ou igual | `temperatura >= 35` |
| `TK_PLUS` | `+` | Soma | `x + 1` |
| `TK_MINUS` | `-` | Subtração (e negativo unário) | `x - 1`, `-x` |
| `TK_STAR` ★ | `*` | Multiplicação | `x * 2` |
| `TK_SLASH` ★ | `/` | Divisão | `x / 2` |

### 1.6 Delimitadores (5)

| Token | Lexema | O que representa | Exemplo |
|---|---|---|---|
| `TK_LBRACE` | `{` | Início de bloco | `{` |
| `TK_RBRACE` | `}` | Fim de bloco | `}` |
| `TK_LPAREN` ★ | `(` | Abre parênteses (parâmetros, chamadas, agrupamento) | `irrigar(10)` |
| `TK_RPAREN` ★ | `)` | Fecha parênteses | `irrigar(10)` |
| `TK_COMMA` ★ | `,` | Separador de parâmetros/argumentos | `media(a, b)` |

### 1.7 Token auxiliar

| Token | Lexema | O que representa |
|---|---|---|
| `TK_EOF` | (fim do arquivo) | Sinaliza ao parser que a entrada acabou |

### 1.8 Elementos ignorados pelo analisador léxico (não geram token)

| Elemento | Padrão | Observação |
|---|---|---|
| Espaço em branco | `espaço`, `tab`, `\r`, `\n` | Só separa tokens |
| Comentário de linha | `#` até o fim da linha | `# isto é um comentário` |

---

## 2. Revisão da lista original

A lista da equipe está bem estruturada (bom uso do tema Minecraft e categorias claras). O que foi ajustado e por quê:

### Correções de inconsistência
- **`lever` aparecia nos exemplos (`lever bomba = true`) mas não existia como token.** Em vez de descartar a ideia, `lever` virou o token `TK_LEVER`, que declara um **atuador** (bomba, ventilador, etc.), par natural de `observer` (sensor). Como um dispositivo físico precisa de um pino, a declaração é `lever bomba = 8`. O exemplo de `TK_TRUE`/`TK_FALSE` passou a usar `craft` (`craft ligado = true`).
- **`TK_IDENTIFIER` e `TK_INTEGER`/`TK_DECIMAL`/`TK_STRING` tinham lexema de exemplo, não padrão.** Na tabela agora aparece o **padrão** (expressão regular em forma legível), que é o que o analisador léxico realmente usa.

### Tokens adicionados (12), necessários para a linguagem funcionar
| Adição | Por que é necessária |
|---|---|
| `TK_LPAREN`, `TK_RPAREN`, `TK_COMMA` | `command` (função) precisa de parâmetros e chamada: `irrigar(10)`, `media(a, b)`. Também servem para agrupar expressões: `(a + b) / 2`. Sem eles a lista original não consegue definir nem chamar funções com argumentos. |
| `TK_AND`, `TK_OR`, `TK_NOT` | Uma fazenda automática quase sempre decide com mais de uma condição (`umidade < 30 and temperatura > 20`). Foram feitos como palavras reservadas (ao estilo Python), o que combina com o restante da linguagem. |
| `TK_NOT_EQUAL`, `TK_LESS_EQUAL`, `TK_GREATER_EQUAL` | A lista original só tinha `==`, `<`, `>`. Comparações do tipo "umidade **>=** 80" são muito comuns em sensores. |
| `TK_STAR`, `TK_SLASH` | Só havia `+` e `-`. Multiplicar e dividir é necessário para converter leituras e calcular médias. |
| `TK_LEVER` | Ver "Correções de inconsistência". |

### Nada foi removido
Todos os 27 tokens originais foram mantidos, sem mudança de nome ou lexema.

### Decisões de projeto (para a equipe confirmar)
- **Sem `;`**: as instruções não terminam com ponto e vírgula; cada instrução começa com uma palavra reservada ou identificador, então a gramática continua sem ambiguidade (ver `documentacao.md`, seção 3.6).
- **Sem acentos em identificadores**: `umidade` sim, `umidáde` não. Acentos são aceitos dentro de strings e comentários.
- **`say` e `wait`**: `wait` usa **segundos** como unidade (regra semântica, não léxica).
- **`observer` / `lever` recebem o pino como expressão** (`observer umidade = 34`); `mine umidade` atualiza o valor do sensor `umidade`, que depois pode ser usado em expressões.
- **Comentários com `#`** (em vez de `//`) para não conflitar com o operador `/`.
