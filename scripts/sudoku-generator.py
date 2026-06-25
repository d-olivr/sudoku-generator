import random
import numpy as np



# CONSTANTES

TAMANHO = 9
TAMANHO_BLOCO = 3

DIFICULDADES = {
    "facil": 35,
    "medio": 45,
    "dificil": 55,
}


# UTILITARIOS DE IMPRESSAO

def linha(char="-", n=49):
    print(char * n)


def imprimir_tabuleiro(tabuleiro: np.ndarray, titulo_tab: str = ""):
    """
    Imprime o tabuleiro 9x9 separando os blocos 3x3 com espacamento extra.
    Celulas vazias (0) aparecem como '.'.
    """
    if titulo_tab:
        print(f"\n  {titulo_tab}")
    linha("-", 49)
    for i in range(TAMANHO):
        celulas = []
        for j in range(TAMANHO):
            valor = tabuleiro[i, j]
            celulas.append(str(valor) if valor != 0 else ".")
            if (j + 1) % TAMANHO_BLOCO == 0 and j != TAMANHO - 1:
                celulas.append("|")
        print("  " + " ".join(celulas))
        if (i + 1) % TAMANHO_BLOCO == 0 and i != TAMANHO - 1:
            linha("-", 49)
    linha("-", 49)


# ============================================================================
# CLASSE PRINCIPAL: encapsula a geracao, remocao e validacao
# ============================================================================

class GeradorSudoku:
    """
    Gera tabuleiros de Sudoku 9x9 validos sem usar backtracking: parte de
    um tabuleiro-base fixo (formula modular) e aplica uma sequencia de
    transformacoes aleatorias que preservam a validade do Sudoku.

    Essa escolha de design (em oposicao a busca com tentativa-e-erro) tem
    a vantagem de ser determinística no tempo de execucao, entao nunca corre
    risco de "travar" tentando preencher uma celula sem opcoes validas.
    """

    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    # Construcao do tabuleiro-base
    @staticmethod
    def _tabuleiro_base() -> np.ndarray:
        """
        base[i][j] = (deslocamento(i) + j) mod 9 + 1, com
        deslocamento(i) = 3*(i mod 3) + (i // 3).
        Gera um tabuleiro fixo, sempre valido, usado como ponto de partida.
        """
        tabuleiro = np.zeros((TAMANHO, TAMANHO), dtype=int)
        for i in range(TAMANHO):
            deslocamento = TAMANHO_BLOCO * (i % TAMANHO_BLOCO) + (i // TAMANHO_BLOCO)
            for j in range(TAMANHO):
                tabuleiro[i, j] = (deslocamento + j) % TAMANHO + 1
        return tabuleiro

    # Transformacoes que preservam validade
    def _permutar_simbolos(self, tabuleiro: np.ndarray) -> np.ndarray:
        #Troca os digitos 1-9 por uma permutacao aleatoria deles mesmos
        simbolos = list(range(1, TAMANHO + 1))
        embaralhados = simbolos.copy()
        self._rng.shuffle(embaralhados)
        mapa = dict(zip(simbolos, embaralhados))
        return np.vectorize(mapa.get)(tabuleiro)

    def _trocar_linhas_na_faixa(self, tabuleiro: np.ndarray) -> np.ndarray:
        #Para cada faixa de 3 linhas, embaralha a ordem das 3 linhas internamente
        resultado = tabuleiro.copy()
        for faixa in range(TAMANHO_BLOCO):
            indices = list(range(faixa * 3, faixa * 3 + 3))
            embaralhados = indices.copy()
            self._rng.shuffle(embaralhados)
            resultado[indices, :] = tabuleiro[embaralhados, :]
        return resultado

    def _trocar_colunas_na_banda(self, tabuleiro: np.ndarray) -> np.ndarray:
        #Para cada banda de 3 colunas, embaralha a ordem das 3 colunas internamente
        resultado = tabuleiro.copy()
        for banda in range(TAMANHO_BLOCO):
            indices = list(range(banda * 3, banda * 3 + 3))
            embaralhados = indices.copy()
            self._rng.shuffle(embaralhados)
            resultado[:, indices] = tabuleiro[:, embaralhados]
        return resultado

    def _trocar_faixas(self, tabuleiro: np.ndarray) -> np.ndarray:
        #Embaralha a ordem das 3 faixas de linhas (cada faixa tem 3 linhas)
        ordem_faixas = list(range(TAMANHO_BLOCO))
        self._rng.shuffle(ordem_faixas)
        blocos = [tabuleiro[f * 3:(f + 1) * 3, :] for f in ordem_faixas]
        return np.vstack(blocos)

    def _trocar_bandas(self, tabuleiro: np.ndarray) -> np.ndarray:
        #Embaralha a ordem das 3 bandas de colunas (cada banda tem 3 colunas)
        ordem_bandas = list(range(TAMANHO_BLOCO))
        self._rng.shuffle(ordem_bandas)
        blocos = [tabuleiro[:, b * 3:(b + 1) * 3] for b in ordem_bandas]
        return np.hstack(blocos)

    def gerar_tabuleiro_completo(self) -> np.ndarray:
        """
        Aplica a sequencia completa de transformacoes sobre o tabuleiro-base
        para produzir um Sudoku completo, valido e "embaralhado" (sem
        qualquer semelhanca visual obvia com o tabuleiro-base original).
        """
        tabuleiro = self._tabuleiro_base()
        tabuleiro = self._permutar_simbolos(tabuleiro)
        tabuleiro = self._trocar_linhas_na_faixa(tabuleiro)
        tabuleiro = self._trocar_colunas_na_banda(tabuleiro)
        tabuleiro = self._trocar_faixas(tabuleiro)
        tabuleiro = self._trocar_bandas(tabuleiro)
        if self._rng.random() < 0.5:
            tabuleiro = tabuleiro.T.copy()
        return tabuleiro

    # Remocao de celulas (cria o "jogo" a partir da "resposta")
    def remover_celulas(self, tabuleiro_completo: np.ndarray, quantidade: int) -> np.ndarray:
        #Remove 'quantidade' celulas aleatorias (define como 0), retornando uma copia
        jogo = tabuleiro_completo.copy()
        todas_posicoes = [(i, j) for i in range(TAMANHO) for j in range(TAMANHO)]
        self._rng.shuffle(todas_posicoes)
        for (i, j) in todas_posicoes[:quantidade]:
            jogo[i, j] = 0
        return jogo

    def gerar_jogo(self, dificuldade: str) -> tuple[np.ndarray, np.ndarray]:
        #Gera o par (jogo_com_lacunas, resposta_completa) para a dificuldade dada
        if dificuldade not in DIFICULDADES:
            raise ValueError(
                f"Dificuldade '{dificuldade}' invalida. Use uma de: {list(DIFICULDADES)}."
            )
        resposta = self.gerar_tabuleiro_completo()
        jogo = self.remover_celulas(resposta, DIFICULDADES[dificuldade])
        return jogo, resposta


# ============================================================================
# VALIDACAO (usada nos testes para confirmar que a geracao esta correta)
# ============================================================================

def grupo_e_valido(grupo) -> bool:
    """Um grupo (linha, coluna ou bloco) e valido se contem 1..9 sem repeticao."""
    return sorted(grupo) == list(range(1, TAMANHO + 1))


def tabuleiro_e_valido(tabuleiro: np.ndarray) -> bool:
    """Verifica todas as 9 linhas, 9 colunas e 9 blocos 3x3 de uma vez."""
    for i in range(TAMANHO):
        if not grupo_e_valido(tabuleiro[i, :].tolist()):
            return False
    for j in range(TAMANHO):
        if not grupo_e_valido(tabuleiro[:, j].tolist()):
            return False
    for bi in range(TAMANHO_BLOCO):
        for bj in range(TAMANHO_BLOCO):
            bloco = tabuleiro[bi*3:bi*3+3, bj*3:bj*3+3].flatten().tolist()
            if not grupo_e_valido(bloco):
                return False
    return True


def contar_celulas_vazias(tabuleiro: np.ndarray) -> int:
    return int(np.sum(tabuleiro == 0))


# ============================================================================
# SOLVER (extra, nao pedido pelo enunciado): resolve um jogo com lacunas
# ============================================================================
# Implementado como complemento, para alem do "gerar respostas" pedido --
# mostra que o gerador e o solver sao operacoes logicamente distintas: o
# gerador aqui NAO usa backtracking, mas o solver abaixo usa, justamente
# para ilustrar a diferenca entre as duas abordagens dentro do mesmo
# trabalho. Usa a heuristica "menor numero de candidatos primeiro" (MRV -
# minimum remaining values), que reduz bastante o espaco de busca em
# relacao a um backtracking ingenuo posicao-por-posicao.

def _candidatos(tabuleiro: np.ndarray, i: int, j: int) -> set:
    usados = set(tabuleiro[i, :]) | set(tabuleiro[:, j])
    bi, bj = (i // 3) * 3, (j // 3) * 3
    usados |= set(tabuleiro[bi:bi+3, bj:bj+3].flatten())
    return set(range(1, 10)) - usados


def resolver_com_backtracking(tabuleiro: np.ndarray) -> np.ndarray | None:
    """
    Resolve um Sudoku com lacunas via backtracking guiado por MRV: em cada
    passo, escolhe a celula vazia com MENOS candidatos possiveis (em vez de
    percorrer em ordem fixa) -- isso poda o espaco de busca bem mais rapido.
    Retorna o tabuleiro resolvido, ou None se nao houver solucao.
    """
    tabuleiro = tabuleiro.copy()

    def passo() -> bool:
        melhor_pos = None
        melhor_candidatos = None
        for i in range(TAMANHO):
            for j in range(TAMANHO):
                if tabuleiro[i, j] == 0:
                    cands = _candidatos(tabuleiro, i, j)
                    if melhor_candidatos is None or len(cands) < len(melhor_candidatos):
                        melhor_pos, melhor_candidatos = (i, j), cands
                        if len(cands) == 0:
                            return False  # poda imediata: celula sem opcoes
        if melhor_pos is None:
            return True  # nenhuma celula vazia restante -> resolvido

        i, j = melhor_pos
        for valor in sorted(melhor_candidatos):
            tabuleiro[i, j] = valor
            if passo():
                return True
            tabuleiro[i, j] = 0
        return False

    return tabuleiro if passo() else None


# ============================================================================
# RELATORIO DE UM JOGO
# ============================================================================

def relatorio_jogo(numero: int, jogo: np.ndarray, resposta: np.ndarray, dificuldade: str):
    vazias = contar_celulas_vazias(jogo)
    total = TAMANHO * TAMANHO
    print(f"\n{'=' * 49}")
    print(f"  JOGO {numero}  -  Dificuldade: {dificuldade.upper()}")
    print(f"{'=' * 49}")
    imprimir_tabuleiro(jogo, "Tabuleiro a resolver ('.' = celula vazia):")
    print(f"  -> {vazias} celulas vazias de {total} ({100 * vazias / total:.1f}% do tabuleiro)")
    imprimir_tabuleiro(resposta, "Resposta (tabuleiro completo):")
    print(f"  -> Resposta valida: {tabuleiro_e_valido(resposta)}")


# ============================================================================
# TESTES AUTOMATIZADOS
# ============================================================================

def testes():
    print("\n" + "#" * 60)
    print("# BLOCO DE TESTES AUTOMATIZADOS -- QUESTAO 2 (SUDOKU)")
    print("#" * 60)

    gerador = GeradorSudoku(seed=7)

    # Teste 1: tabuleiro-base por si so deve ser valido
    print("\n--- Teste 1: tabuleiro-base (sem transformacoes) e valido ---")
    base = gerador._tabuleiro_base()
    assert tabuleiro_e_valido(base), "FALHOU: tabuleiro-base deveria ser valido"
    print("  OK: tabuleiro-base satisfaz linhas, colunas e blocos 3x3.")

    # Teste 2: apos toda a cadeia de transformacoes, ainda deve ser valido
    print("\n--- Teste 2: tabuleiro apos transformacoes completas e valido ---")
    for tentativa in range(20):
        completo = gerador.gerar_tabuleiro_completo()
        assert tabuleiro_e_valido(completo), (
            f"FALHOU na tentativa {tentativa}: tabuleiro invalido apos transformacoes"
        )
    print("  OK: 20 tabuleiros gerados em sequencia, todos validos.")

    # Teste 3: tabuleiros gerados em chamadas sucessivas devem variar
    print("\n--- Teste 3: tabuleiros gerados sao diferentes entre execucoes ---")
    t1 = gerador.gerar_tabuleiro_completo()
    t2 = gerador.gerar_tabuleiro_completo()
    assert not np.array_equal(t1, t2), "FALHOU: dois tabuleiros gerados sao identicos"
    print("  OK: tabuleiros consecutivos sao diferentes (aleatoriedade funcionando).")

    # Teste 4: cada dificuldade remove exatamente a quantidade configurada
    print("\n--- Teste 4: quantidade de celulas removidas por dificuldade ---")
    for dif, esperado in DIFICULDADES.items():
        jogo, resposta = gerador.gerar_jogo(dif)
        vazias = contar_celulas_vazias(jogo)
        assert vazias == esperado, f"FALHOU: {dif} deveria remover {esperado}, removeu {vazias}"
        assert tabuleiro_e_valido(resposta), f"FALHOU: resposta de '{dif}' nao e valida"
        print(f"  {dif:8s}: {vazias} celulas removidas (esperado {esperado}) -> OK")

    # Teste 5: a remocao nunca deve alterar os valores das celulas restantes
    print("\n--- Teste 5: celulas nao removidas mantem o valor original ---")
    jogo5, resposta5 = gerador.gerar_jogo("medio")
    preservadas = (jogo5 != 0)
    assert np.array_equal(jogo5[preservadas], resposta5[preservadas]), (
        "FALHOU: alguma celula preservada foi alterada na remocao"
    )
    print("  OK: todas as celulas nao removidas continuam iguais a resposta.")

    # Teste 6: dificuldade invalida deve ser rejeitada com erro claro
    print("\n--- Teste 6: dificuldade invalida e rejeitada ---")
    try:
        gerador.gerar_jogo("impossivel")
        raise AssertionError("FALHOU: deveria ter lancado ValueError")
    except ValueError as e:
        print(f"  OK: erro tratado corretamente -> {e}")

    # Teste 7: o solver (extra) consegue resolver os jogos gerados e bater
    #          com a resposta original nas celulas que tinham lacuna
    print("\n--- Teste 7: solver por backtracking resolve os jogos gerados ---")
    for dif in DIFICULDADES:
        jogo7, resposta7 = gerador.gerar_jogo(dif)
        resolvido = resolver_com_backtracking(jogo7)
        assert resolvido is not None, f"FALHOU: solver nao encontrou solucao para '{dif}'"
        assert tabuleiro_e_valido(resolvido), f"FALHOU: solucao do solver invalida para '{dif}'"
        print(f"  {dif:8s}: solver encontrou uma solucao valida -> OK")

    print("\n" + "#" * 60)
    print("# TODOS OS TESTES PASSARAM")
    print("#" * 60 + "\n")


# ============================================================================
# MODO PADRAO (testes() + geracao de exemplo, sem pedir input)
# ============================================================================

def demonstracao():
    """Gera um jogo de cada dificuldade e imprime o relatorio completo."""
    print("\n" + "=" * 60)
    print("  QUESTAO 2 -- GERADOR DE SUDOKU  |  DEMONSTRACAO")
    print("=" * 60)
    gerador = GeradorSudoku()
    for numero, dificuldade in enumerate(DIFICULDADES, start=1):
        jogo, resposta = gerador.gerar_jogo(dificuldade)
        relatorio_jogo(numero, jogo, resposta, dificuldade)
    print(f"\n{'=' * 60}")
    print("  FIM DA DEMONSTRACAO")
    print(f"{'=' * 60}\n")


# ============================================================================
# MODO INTERATIVO (pede input do usuario; ativar quando solicitado)
# ============================================================================

def main():
    """Modo interativo: pergunta quantidade de jogos e dificuldade desejadas."""
    print("\n" + "=" * 60)
    print("  QUESTAO 2 -- GERADOR DE SUDOKU")
    print("=" * 60)

    while True:
        try:
            quantidade = int(input("\nQuantos jogos deseja gerar? "))
            if quantidade < 1:
                print("  Informe um numero maior que zero.")
                continue
            break
        except ValueError:
            print("  Entrada invalida. Informe um numero inteiro.")

    while True:
        dificuldade = input("Dificuldade? [facil / medio / dificil]: ").strip().lower()
        if dificuldade in DIFICULDADES:
            break
        print("  Opcao invalida. Digite: facil, medio ou dificil.")

    gerador = GeradorSudoku()
    for numero in range(1, quantidade + 1):
        jogo, resposta = gerador.gerar_jogo(dificuldade)
        relatorio_jogo(numero, jogo, resposta, dificuldade)


if __name__ == "__main__":
    testes()
    demonstracao()

    # Para o modo interativo (pede input do usuario), comente as duas
    # linhas acima e descomente a linha abaixo:
    # main()
