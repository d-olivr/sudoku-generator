<div align="center">

# 🎲 Sudoku Generator
### *Geração de tabuleiros 9×9 válidos, sem backtracking*

**Projeto de Álgebra Linear Computacional · UFRRJ**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![NumPy](https://img.shields.io/badge/NumPy-Manipulação_de_Matrizes-013243?style=flat-square&logo=numpy&logoColor=white)](https://numpy.org)
[![Google Colab](https://img.shields.io/badge/Google_Colab-Notebook-F9AB00?style=flat-square&logo=googlecolab&logoColor=white)](https://colab.research.google.com)
[![Status](https://img.shields.io/badge/Status-Completo-brightgreen?style=flat-square)]()

</div>

---

## 📌 Overview

Gerador de jogos de Sudoku 9×9 (com respostas), feito para a Questão 2 da Segunda Prova de Álgebra Linear Computacional

A particularidade deste projeto: a **geração do tabuleiro completo não usa backtracking**. Em vez de tentativa-e-erro, ela parte de um tabuleiro-base fixo (construído por uma fórmula fechada) e aplica uma cadeia de transformações que **sempre preservam a validade** de um Sudoku - o resultado final parece facultativo, mas é garantido ser correto, sem risco de travar durante a geração

Disponível em duas versões equivalentes:
- **`scripts/questao2_sudoku.py`** - script standalone, roda em qualquer ambiente Python
- **`notebooks/questao2_sudoku.ipynb`** - mesma lógica mas em células, pensado para o Google Colab, com explicações em markdown intercaladas com o código. Esse é o arquivo que de fato enviei para o professor

---

## 🧩 Como funciona a geração

Um tabuleiro-base sempre válido é construído com a fórmula:

```
base[i][j] = ( deslocamento(i) + j ) mod 9 + 1
deslocamento(i) = 3·(i mod 3) + (i // 3)
```

Essa fórmula garante automaticamente que cada linha, cada coluna e cada bloco 3x3 contenham os 9 dígitos, sem repetição 

A partir desse tabuleiro-base fixo, as seguintes operações **sempre** preservam a validade do Sudoku (por isso podem ser aplicadas em qualquer combinação/ordem e com qualquer aleatoriedade):

1. Permutar os símbolos 1–9 (trocar todo "3" por "7", etc.);
2. Trocar duas linhas **dentro** da mesma faixa de 3 linhas;
3. Trocar duas colunas **dentro** da mesma banda de 3 colunas;
4. Trocar duas faixas de 3 linhas entre si;
5. Trocar duas bandas de 3 colunas entre si;
6. Transpor o tabuleiro (trocar linhas por colunas).

Aplicando essas operações em sequência aleatória, o tabuleiro final parece arbitrário, mas é garantidamente válido.

### Remoção de células (cria o "jogo" a partir da "resposta")

| Dificuldade | Células removidas | % do tabuleiro vazio |
|---|---|---|
| `facil` | 35 | ~43% |
| `medio` | 45 | ~56% |
| `dificil` | 55 | ~68% |

A remoção é puramente aleatória sobre o tabuleiro completo - não há garantia de solução única após a remoção, mas como a resposta é entregue junto do jogo, isso não afeta o uso didático pedido para o projeto.

---

## ➕ Extra: solver via backtracking 

Para evidenciar que **gerar** e **resolver** um Sudoku são problemas logicamente diferentes, o repositório inclui também um *solver* que usa backtracking de fato - ao contrário do gerador, que não faz busca alguma.

O solver usa a heurística **MRV** (*minimum remaining values*): em cada passo, escolhe a célula vazia com **menos candidatos possíveis** (em vez de percorrer em ordem fixa linha por linha), o que poda bastante o espaço de busca em relação a um backtracking naive.

---

## 📐 Hipóteses assumidas

- O Sudoku gerado é o clássico 9x9, dividido em 9 blocos 3x3;
- A geração do tabuleiro completo é determinística no tempo de execução (não há tentativa-e-erro);
- A remoção de células não garante solução única do jogo resultante, apenas garante que a resposta entregue é válida;
- O ponto de entrada padrão (`testes()` + `demonstracao()`) não pede input do usuário; o modo interativo (`main()`) pede quantidade de jogos e dificuldade via `input()`.

A documentação completa de hipóteses está nos comentários no topo de cada arquivo (`.py` e primeira célula do `.ipynb`).

---

## 🗂️ Estrutura do Projeto

```
sudoku-generator/
│
├── notebooks/
│   └── 📓 sudoku-generator.ipynb
│
├── scripts/
│   └── 🐍 sudoku-generator.py
│
├── requirements.txt
└── README.md
```

---

## ✅ Testes e validação

O script roda uma bateria de 7 testes automatizados (`testes()`) como ponto de entrada padrão, sem precisar de input do usuário:

1. O tabuleiro-base (sem nenhuma transformação) já é válido por si só
2. 20 tabuleiros gerados em sequência, todos válidos após a cadeia completa de transformações
3. Tabuleiros gerados em chamadas sucessivas são diferentes entre si
4. Cada dificuldade remove exatamente a quantidade de células configurada
5. Células não removidas mantêm o valor original da resposta
6. Dificuldade inválida é rejeitada com erro claro
7. O solver extra resolve corretamente os jogos gerados em todas as dificuldades

---

## 🛠️ Tecnologias

| Tool | Finalidade |
|------|------------|
| **Python 3.11+** | Linguagem principal |
| **NumPy** | Manipulação de matrizes (tabuleiro como array 9×9) |
| **random** (stdlib) | Aleatoriedade controlada por seed nas transformações e remoções |
| **Google Colab** | Ambiente de execução do notebook |

---

## 🚀 Como rodar

```bash
# Clonar o repositório
git clone https://github.com/SEU_USUARIO/sudoku-generator.git
cd sudoku-generator

# Instalar dependências
pip install -r requirements.txt

# Rodar o script (executa os testes automaticamente e depois a demonstração)
python scripts/questao2_sudoku.py
```

Ou abra `notebooks/questao2_sudoku.ipynb` direto no Google Colab (`Arquivo -> Fazer upload de notebook`).

Para o modo interativo (escolher quantidade de jogos e dificuldade), comente as chamadas a `testes()`/`demonstracao()` no final do script e descomente a chamada a `main()`.

---

## 🤖 Uso de LLM

Conforme exigido no enunciado do trabalho, o uso de LLM (nesse caso, o Claude, da Anthropic) está declarado diretamente nos comentários do topo de `sudoku-generator.py` e na primeira célula do notebook, detalhando especificamente em que pontos a IA foi utilizada para o projeto (revisão da corretude das transformações, organização do fluxo interativo/de testes). Apesar da ajuda extra da ferramenta, o raciocínio sobre por que cada transformação preserva a validade de um Sudoku foi entendido e validado manualmente. :)

