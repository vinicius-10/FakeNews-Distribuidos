"""
Versão paralela da simulação.

Divisão do trabalho
-------------------
A grade é dividida em faixas horizontais de linhas contíguas, uma por worker
(comum.modelo.dividir_em_faixas). Cada worker calcula só as linhas da sua faixa.

Memória
-------
- modo "processos" (padrão): as duas grades (geração atual e próxima) ficam em
  blocos de multiprocessing.shared_memory. Todos os processos enxergam os
  mesmos bytes, sem copiar a grade a cada geração. Processos são necessários
  porque, no CPython 3.12, o GIL impede que threads executem Python ao mesmo
  tempo (o enunciado permite multiprocessing no lugar de threading);
- modo "threads": o mesmo laço, com threads e bytearrays comuns. Existe para o
  experimento que mostra o efeito do GIL.

Sincronização (modelo BSP: cada geração é um superpasso)
--------------------------------------------------------
1. cada worker lê a grade atual e escreve a sua faixa na grade nova;
2. conta os estados da sua faixa e grava no seu índice de `contagens`;
3. barreira A: o principal espera todos terminarem;
4. o principal soma as contagens (redução), imprime e decide se continua;
5. barreira B: os workers esperam a decisão;
6. todos trocam o papel das grades (só a referência, sem cópia).

Por que não há condição de corrida: durante o cálculo, a grade atual só é lida
e cada worker escreve apenas as linhas da própria faixa na grade nova; ninguém
escreve na grade que será lida antes de todos passarem pela barreira. Cada
worker escreve só o seu trecho de `contagens`, e o principal só lê depois da
barreira A. `continuar` só é escrito pelo principal, entre as barreiras A e B.

Uso: python -m paralelo.fakenews_paralelo --linhas 1000 --colunas 1000 --limiar 2 --trabalhadores 8
"""

import multiprocessing as mp
import os
import queue
import threading
import time
import traceback
from multiprocessing import shared_memory
from types import SimpleNamespace

from comum import modelo
from comum.estatisticas import Estatisticas
from comum.parametros import novo_parser, parametros_de_argumentos, preparar_estado_inicial
from comum.saida import imprimir_cabecalho, imprimir_geracao, imprimir_grade, imprimir_resultado
from comum.visualizacao import Animacao

TIMEOUT_PADRAO = 600  # segundos; uma barreira presa vira erro em vez de travar


def laco_trabalhador(ident, buffers, limiares, colunas, inicio, fim, limiar, geracoes,
                     barreira, contagens, continuar, resultados):
    """
    Laço de um worker, igual nos modos processos e threads.

    buffers são as duas grades (com moldura); inicio/fim são as linhas reais da
    faixa (fim exclusivo). Ao terminar, envia (ident, tempo de cálculo, tempo de
    espera, erro) pela fila `resultados`.
    """
    calculo = espera = 0.0
    try:
        barreira.wait()  # largada: todos começam juntos, depois de criados
        for geracao in range(1, geracoes + 1):
            t0 = time.perf_counter()
            atual = buffers[(geracao - 1) % 2]
            nova = buffers[geracao % 2]
            # +1: a linha real r fica na linha r + 1 do vetor (moldura).
            modelo.calcular_faixa(atual, nova, colunas, inicio + 1, fim + 1, limiar, limiares)
            contagens[4 * ident:4 * ident + 4] = modelo.contar_faixa(nova, colunas,
                                                                      inicio + 1, fim + 1)
            t1 = time.perf_counter()
            barreira.wait()  # A: a faixa e a contagem desta geração estão prontas
            barreira.wait()  # B: o principal já decidiu se continua
            t2 = time.perf_counter()
            calculo += t1 - t0
            espera += t2 - t1
            if not continuar.value:
                break
        resultados.put((ident, calculo, espera, None))
    except Exception:  # noqa: BLE001 - qualquer erro precisa destravar os outros
        # Quebrar a barreira faz os outros receberem BrokenBarrierError na
        # hora, em vez de esperarem o timeout.
        barreira.abort()
        resultados.put((ident, calculo, espera, traceback.format_exc()))


def processo_trabalhador(ident, nomes, tamanho, nome_limiares, colunas, inicio, fim, limiar,
                         geracoes, barreira, contagens, continuar, resultados):
    """
    Ponto de entrada de cada processo (no nível do módulo para funcionar com spawn).

    Conecta-se aos blocos de memória compartilhada pelo nome e roda o laço.
    """
    blocos = [shared_memory.SharedMemory(name=nome) for nome in nomes]
    bloco_limiares = shared_memory.SharedMemory(name=nome_limiares) if nome_limiares else None
    # No Windows o bloco pode ser maior que o pedido (arredondado para páginas),
    # por isso as views são cortadas no tamanho exato.
    views = [bloco.buf[:tamanho] for bloco in blocos]
    view_limiares = bloco_limiares.buf[:tamanho] if bloco_limiares else None
    try:
        laco_trabalhador(ident, views, view_limiares, colunas, inicio, fim, limiar, geracoes,
                         barreira, contagens, continuar, resultados)
    finally:
        # As views precisam ser liberadas antes de fechar o bloco.
        for view in views:
            view.release()
        if view_limiares is not None:
            view_limiares.release()
        for bloco in blocos + ([bloco_limiares] if bloco_limiares else []):
            bloco.close()


class _Recursos:
    """Cria as estruturas compartilhadas de cada modo e as libera no fim."""

    def __init__(self, modo, grade, limiares, trabalhadores, timeout):
        self.modo = modo
        self.blocos = []
        self.views = []
        tamanho = len(grade)
        if modo == "processos":
            # spawn explícito: mesmo comportamento no Windows e no Linux.
            self.ctx = mp.get_context("spawn")
            # Grade atual (inicial) e grade próxima, que começa zerada; a
            # moldura de zeros das duas nunca é escrita depois.
            self.buffers = [self._novo_bloco(grade), self._novo_bloco(bytes(tamanho))]
            self.limiares = self._novo_bloco(limiares) if limiares is not None else None
            self.contagens = self.ctx.Array("q", 4 * trabalhadores, lock=False)
            self.continuar = self.ctx.Value("b", 1, lock=False)
            self.barreira = self.ctx.Barrier(trabalhadores + 1, timeout=timeout)
            self.resultados = self.ctx.Queue()
        else:
            self.buffers = [bytearray(grade), bytearray(tamanho)]
            self.limiares = limiares
            self.contagens = [0] * (4 * trabalhadores)
            self.continuar = SimpleNamespace(value=1)
            self.barreira = threading.Barrier(trabalhadores + 1, timeout=timeout)
            self.resultados = queue.Queue()

    def _novo_bloco(self, conteudo):
        """Cria um bloco de memória compartilhada com uma cópia de `conteudo`."""
        bloco = shared_memory.SharedMemory(create=True, size=len(conteudo))
        view = bloco.buf[:len(conteudo)]
        view[:] = conteudo
        self.blocos.append(bloco)
        self.views.append(view)
        return view

    def nomes(self):
        """Nomes dos blocos (grades e, se houver, limiares) para os processos."""
        return [b.name for b in self.blocos[:2]], (self.blocos[2].name if len(self.blocos) == 3
                                                  else None)

    def liberar(self):
        """Libera views e blocos; unlink só aqui, uma vez, pelo processo principal."""
        for view in self.views:
            view.release()
        for bloco in self.blocos:
            bloco.close()
            bloco.unlink()


def executar_simulacao(parametros, trabalhadores=None, modo="processos", mostrar=True,
                       mostrar_grade=False, ao_fim_da_geracao=None, estatisticas=None,
                       animacao=None, timeout=TIMEOUT_PADRAO):
    """
    Executa a simulação dividindo as faixas entre `trabalhadores` workers.

    Mesma interface da versão sequencial refatorada, mais o número de workers e
    o modo ("processos" ou "threads"). Devolve o mesmo dicionário de resultado.
    """
    if modo not in ("processos", "threads"):
        raise ValueError("modo deve ser 'processos' ou 'threads'")
    trabalhadores = trabalhadores or os.cpu_count() or 1
    linhas, colunas = parametros.linhas, parametros.colunas
    # A grade inicial é gerada uma vez só, aqui, e depois dividida.
    grade, limiares = preparar_estado_inicial(parametros)
    contagem = modelo.contar_faixa(grade, colunas, 1, linhas + 1)
    faixas = modelo.dividir_em_faixas(linhas, trabalhadores)

    if mostrar:
        imprimir_cabecalho("PARALELA", parametros, contagem,
                           [f"Modo: {modo} | Trabalhadores: {trabalhadores}"])
    if animacao is not None:
        animacao.adicionar(0, grade)

    inicio_total = time.perf_counter()
    rec = _Recursos(modo, grade, limiares, trabalhadores, timeout)
    workers = []
    try:
        for ident, (ini, fim) in enumerate(faixas):
            argumentos = (rec.contagens, rec.continuar, rec.resultados)
            comuns = (colunas, ini, fim, parametros.limiar, parametros.geracoes, rec.barreira)
            if modo == "processos":
                nomes, nome_limiares = rec.nomes()
                w = rec.ctx.Process(target=processo_trabalhador,
                                    args=(ident, nomes, len(grade), nome_limiares) + comuns
                                    + argumentos, name=f"worker-{ident}")
            else:
                w = threading.Thread(target=laco_trabalhador,
                                     args=(ident, rec.buffers, rec.limiares) + comuns
                                     + argumentos, name=f"worker-{ident}", daemon=True)
            w.start()
            workers.append(w)
        fim_vigia = threading.Event()
        if modo == "processos":
            threading.Thread(target=_vigiar_processos, args=(workers, rec.barreira, fim_vigia),
                             daemon=True).start()

        geracoes_executadas = 0
        try:
            rec.barreira.wait()  # largada: o tempo do laço não inclui criar processos
            inicio = time.perf_counter()
            for geracao in range(1, parametros.geracoes + 1):
                rec.barreira.wait()  # A: todas as faixas desta geração prontas
                geracoes_executadas = geracao
                contagem = [sum(rec.contagens[estado::4]) for estado in range(4)]
                # Entre A e B os workers estão parados: ler a grade aqui é seguro.
                nova = rec.buffers[geracao % 2]
                if mostrar:
                    imprimir_geracao(geracao, contagem)
                    if mostrar_grade:
                        imprimir_grade(nova, linhas, colunas)
                if estatisticas is not None:
                    estatisticas.registrar_geracao(geracao, contagem)
                if animacao is not None:
                    animacao.adicionar(geracao, nova)
                if ao_fim_da_geracao is not None:
                    ao_fim_da_geracao(geracao, bytes(nova))
                vivo = contagem[modelo.ESPALHADOR] + contagem[modelo.BOT] > 0
                rec.continuar.value = 1 if vivo and geracao < parametros.geracoes else 0
                rec.barreira.wait()  # B: libera os workers com a decisão tomada
                if not vivo:
                    if mostrar:
                        print("\nA propagação terminou: não há mais espalhadores.")
                    break
            tempo = time.perf_counter() - inicio
        except threading.BrokenBarrierError:
            raise RuntimeError("um worker falhou:\n" + _erros_dos_workers(rec)) from None

        perfis = sorted(rec.resultados.get(timeout=timeout) for _ in workers)
        for w in workers:
            w.join(timeout)
        erros = [erro for *_, erro in perfis if erro]
        if erros:
            raise RuntimeError("um worker falhou:\n" + "\n".join(erros))
        grade_final = bytes(rec.buffers[geracoes_executadas % 2])
    finally:
        if workers:
            fim_vigia.set()
        for w in workers:
            if modo == "processos" and w.is_alive():
                w.terminate()
        rec.liberar()
    tempo_total = time.perf_counter() - inicio_total

    if estatisticas is not None:
        estatisticas.tempo_laco = tempo
        estatisticas.tempo_total = tempo_total
        for ident, calculo, espera, _ in perfis:
            # Em memória compartilhada não há troca de mensagens: comunicação = 0.
            estatisticas.registrar_trabalhador(ident, calculo, 0.0, espera)
    if mostrar:
        imprimir_resultado(tempo, contagem, linhas * colunas, tempo_total)
    return {"grade": grade_final, "contagem": contagem,
            "geracoes_executadas": geracoes_executadas, "tempo_laco": tempo,
            "tempo_total": tempo_total}


def _vigiar_processos(workers, barreira, fim):
    """
    Aborta a barreira se algum processo morrer sem avisar.

    Um processo que morre antes de entrar no laço (por exemplo, erro de import
    no spawn) nunca chega à barreira, e o principal esperaria até o timeout.
    Esta thread confere os processos a cada meio segundo e quebra a barreira,
    o que transforma a espera em erro imediato.
    """
    while not fim.wait(0.5):
        if any(w.exitcode not in (None, 0) for w in workers):
            barreira.abort()
            return


def _erros_dos_workers(rec):
    """Junta as mensagens de erro que os workers mandaram antes de abortar."""
    mensagens = []
    try:
        while True:
            *_, erro = rec.resultados.get(timeout=2)
            if erro:
                mensagens.append(erro)
    except queue.Empty:
        pass
    return "\n".join(mensagens) or "barreira expirou (timeout) sem mensagem de erro"


def main(argv=None):
    """Lê os argumentos da linha de comando e executa."""
    parser = novo_parser("Simulação paralela de propagação de fake news")
    parser.add_argument("--trabalhadores", type=int, default=os.cpu_count(),
                        help="número de processos/threads (padrão: núcleos lógicos)")
    parser.add_argument("--modo", choices=("processos", "threads"), default="processos")
    parser.add_argument("--timeout", type=float, default=TIMEOUT_PADRAO,
                        help="segundos máximos de espera numa barreira")
    args = parser.parse_args(argv)
    parametros = parametros_de_argumentos(args)
    estatisticas = (Estatisticas(f"paralela_{args.modo}", parametros, args.trabalhadores)
                    if args.estatisticas else None)
    animacao = (Animacao(parametros.linhas, parametros.colunas, "paralela")
                if args.animacao else None)
    executar_simulacao(parametros, args.trabalhadores, args.modo,
                       mostrar_grade=args.mostrar_grade, estatisticas=estatisticas,
                       animacao=animacao, timeout=args.timeout)
    if estatisticas is not None:
        estatisticas.imprimir_resumo()
        print(f"Estatísticas gravadas em {estatisticas.salvar(args.estatisticas)}")
    if animacao is not None:
        print(f"Animação gravada em {animacao.salvar(args.animacao)}")


if __name__ == "__main__":
    main()
