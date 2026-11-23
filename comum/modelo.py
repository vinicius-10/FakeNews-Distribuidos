"""
Núcleo do autômato celular, compartilhado pelas três versões.

Representação da grade
----------------------
A grade de L x C células vira um vetor de bytes (bytearray ou memória
compartilhada), 1 byte por célula, linha após linha. Em volta dela há uma
MOLDURA de uma linha de zeros em cima e uma embaixo, então o vetor tem
(L + 2) * C bytes e a linha real r da grade fica na linha r + 1 do vetor.

Por que a moldura:
- zero é IGNORANTE, que não conta como espalhador; uma linha de zeros fora da
  grade tem o mesmo efeito das bordas fixas do professor (vizinho fora da grade
  não conta), sem precisar testar o limite das linhas no laço;
- na versão distribuída, cada worker guarda só a sua faixa e usa essas duas
  linhas extras como "halo" (células fantasmas) com as bordas dos vizinhos.
  Assim o mesmo cálculo serve para a grade inteira e para uma faixa.

As colunas continuam com teste de limite, como no código do professor.

Por que um vetor de bytes e não lista de listas: ele pode ser colocado em
memória compartilhada entre processos e enviado por socket sem conversão, e a
troca de buffers entre gerações é só trocar referências, sem o deepcopy do
original (melhoria "grade compacta").
"""

import random

from sequencial.fakenews_sequencial_original import (
    ESPALHADOR,
    IGNORANTE,
    INATIVO,
    criar_grade,
)

# Melhoria "bots": célula que espalha sempre e nunca fica inativa.
BOT = 3

# Para cada estado, quanto ele soma na contagem de vizinhos espalhadores.
# Indexar uma tupla é mais simples de ler que um "if" com dois casos.
CONTA_COMO_ESPALHADOR = (0, 1, 0, 1)  # IGNORANTE, ESPALHADOR, INATIVO, BOT

__all__ = [
    "IGNORANTE", "ESPALHADOR", "INATIVO", "BOT", "CONTA_COMO_ESPALHADOR",
    "criar_grade_inicial", "criar_limiares", "grade_para_plana", "plana_para_lista",
    "dividir_em_faixas", "calcular_faixa", "contar_faixa", "empacotar_bits",
    "desempacotar_bits",
]


# ---------------------------------------------------------------------------
# Estado inicial (gerado uma vez só, pelo processo principal ou coordenador)
# ---------------------------------------------------------------------------

def criar_grade_inicial(linhas, colunas, percentual_espalhadores, semente=42, fracao_bots=0.0):
    """
    Cria a grade inicial como lista de listas.

    Sem bots, é exatamente a grade do professor (mesma função, mesma semente).
    Com bots, sorteia as posições com um gerador próprio (semente + 2), para não
    alterar a sequência de sorteios do professor.
    """
    grade = criar_grade(linhas, colunas, percentual_espalhadores, semente)
    if fracao_bots > 0:
        sorteio = random.Random(semente + 2)
        for _ in range(int(linhas * colunas * fracao_bots)):
            grade[sorteio.randint(0, linhas - 1)][sorteio.randint(0, colunas - 1)] = BOT
    return grade


def criar_limiares(linhas, colunas, minimo, maximo, semente=42):
    """
    Melhoria "resistência individual": sorteia um limiar para cada célula.

    Cada pessoa precisa de um número diferente de vizinhos espalhadores para ser
    convencida, entre minimo e maximo (inclusive). Usa um gerador próprio
    (semente + 1) para ser reproduzível sem mexer nos sorteios da grade.
    """
    sorteio = random.Random(semente + 1)
    return [[sorteio.randint(minimo, maximo) for _ in range(colunas)] for _ in range(linhas)]


def grade_para_plana(grade):
    """Converte lista de listas em vetor de bytes com a moldura de zeros."""
    colunas = len(grade[0])
    plana = bytearray(colunas)  # linha de moldura de cima
    for linha in grade:
        plana.extend(linha)
    plana.extend(bytes(colunas))  # linha de moldura de baixo
    return plana


def plana_para_lista(plana, linhas, colunas):
    """Converte o vetor de bytes (com moldura) de volta para lista de listas."""
    return [list(plana[(i + 1) * colunas:(i + 2) * colunas]) for i in range(linhas)]


def dividir_em_faixas(linhas, partes):
    """
    Divide as linhas da grade em `partes` faixas contíguas.

    Devolve [(inicio, fim), ...] em linhas reais (0 a linhas), com fim exclusivo.
    Os tamanhos diferem no máximo em 1 linha; se houver mais partes que linhas,
    algumas faixas ficam vazias (inicio == fim).
    """
    return [(p * linhas // partes, (p + 1) * linhas // partes) for p in range(partes)]


# ---------------------------------------------------------------------------
# Cálculo de uma geração
# ---------------------------------------------------------------------------

def calcular_faixa(atual, nova, colunas, linha_ini, linha_fim, limiar, limiares=None):
    """
    Calcula a próxima geração das linhas [linha_ini, linha_fim) do vetor.

    As linhas são índices no vetor com moldura (a linha real r é a r + 1).
    Lê só `atual` (as linhas da faixa e uma acima e uma abaixo) e escreve só as
    linhas da faixa em `nova`. É essa separação (buffer duplo) que permite
    várias faixas serem calculadas ao mesmo tempo sem condição de corrida.

    Regras (as do professor, mais as melhorias, que só agem se estiverem na grade):
    - ignorante vira espalhador com pelo menos `limiar` vizinhos espalhadores
      (ou o limiar da própria célula, se `limiares` for dado);
    - espalhador vira inativo; inativo continua inativo;
    - bot continua bot (e conta como espalhador para os vizinhos).
    """
    conta = CONTA_COMO_ESPALHADOR
    ultima_coluna = colunas - 1
    for i in range(linha_ini, linha_fim):
        acima = (i - 1) * colunas
        meio = i * colunas
        abaixo = (i + 1) * colunas
        for j in range(colunas):
            k = meio + j
            estado = atual[k]
            if estado == IGNORANTE:
                # Vizinhança de Moore: 3 células na linha de cima, 2 na própria
                # linha e 3 na de baixo. A moldura cobre as bordas de cima e de
                # baixo; as bordas laterais são tratadas pelos testes de j.
                total = conta[atual[acima + j]] + conta[atual[abaixo + j]]
                if j > 0:
                    total += (conta[atual[acima + j - 1]] + conta[atual[k - 1]]
                              + conta[atual[abaixo + j - 1]])
                if j < ultima_coluna:
                    total += (conta[atual[acima + j + 1]] + conta[atual[k + 1]]
                              + conta[atual[abaixo + j + 1]])
                necessario = limiar if limiares is None else limiares[k]
                nova[k] = ESPALHADOR if total >= necessario else IGNORANTE
            elif estado == ESPALHADOR:
                nova[k] = INATIVO
            else:
                # Inativo continua inativo e bot continua bot.
                nova[k] = estado


def contar_faixa(grade, colunas, linha_ini, linha_fim):
    """
    Conta os estados das linhas [linha_ini, linha_fim) do vetor com moldura.

    Devolve [ignorantes, espalhadores, inativos, bots]. Cada worker conta a sua
    faixa e o processo principal soma (redução), em vez de alguém percorrer a
    grade inteira de novo.
    """
    trecho = bytes(grade[linha_ini * colunas:linha_fim * colunas])
    return [trecho.count(IGNORANTE), trecho.count(ESPALHADOR),
            trecho.count(INATIVO), trecho.count(BOT)]


# ---------------------------------------------------------------------------
# Melhoria "borda compactada em bits" (versão distribuída)
# ---------------------------------------------------------------------------

def empacotar_bits(grade, inicio, colunas):
    """
    Compacta uma linha da grade em 1 bit por célula: 1 se conta como espalhador.

    Para calcular a faixa vizinha só importa se cada célula da borda é ou não
    espalhadora (o estado dela não é recalculado por quem recebe), então 1 bit
    basta e a mensagem fica 8 vezes menor que 1 byte por célula.
    """
    conta = CONTA_COMO_ESPALHADOR
    dados = bytearray((colunas + 7) // 8)
    for j in range(colunas):
        if conta[grade[inicio + j]]:
            dados[j >> 3] |= 1 << (j & 7)
    return bytes(dados)


def desempacotar_bits(dados, destino, inicio, colunas):
    """
    Expande uma linha compactada em bits para 1 byte por célula em `destino`.

    Grava ESPALHADOR onde o bit é 1 e IGNORANTE onde é 0. É o suficiente para o
    halo, que só é lido na contagem de vizinhos.
    """
    for j in range(colunas):
        destino[inicio + j] = ESPALHADOR if dados[j >> 3] >> (j & 7) & 1 else IGNORANTE
