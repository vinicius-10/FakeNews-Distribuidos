# 🗺️ Andamento do trabalho

O que já foi feito e o que falta para a entrega final. **Quem concluir uma etapa atualiza este
arquivo** (tabela, checklist e histórico) no mesmo PR.

Última atualização: **23 nov. 2026**.

## Resumo

| Entrega | Situação | Onde |
|---|---|---|
| Sequencial original (professor) | ✅ referência, não alterar | [`sequencial/fakenews_sequencial_original.py`](../sequencial/fakenews_sequencial_original.py) |
| Sequencial refatorada | ✅ feita e testada | [`sequencial/fakenews_sequencial.py`](../sequencial/fakenews_sequencial.py) + [`comum/`](../comum/) |
| Paralela (processos e threads) | ✅ feita e testada | [`paralelo/fakenews_paralelo.py`](../paralelo/fakenews_paralelo.py) |
| Distribuída (sockets TCP) | ✅ feita e testada | [`distribuido/`](../distribuido/) |
| Testes de equivalência | ✅ 27 testes passando | [`testes/`](../testes/) |
| 6 melhorias | ✅ implementadas · ❌ não medidas · ❌ não escritas no relatório | [seção 5](#5-melhorias-escolhidas) |
| Experimentos de desempenho | ❌ não começados | — |
| Relatório (Overleaf) | 🔄 fundamentação avançou; o resto tem `\todo` | [`relatorio/`](../relatorio/) (cópia) |
| Slides (PDF) | ❌ não começados | — |
| Vídeo 10–15 min | ❌ não gravado | — |
| ZIP final | ❌ | — |

---

## 1. Refatoração (núcleo comum)

A sequencial do professor ficou intacta. As três versões novas usam o mesmo núcleo em
[`comum/`](../comum/): só muda **como o trabalho é dividido**, não a regra da simulação.

| Arquivo | Papel |
|---|---|
| `comum/modelo.py` | grade em vetor de bytes com moldura, cálculo de uma faixa, contagem, divisão em faixas, borda em bits |
| `comum/parametros.py` | parâmetros e linha de comando comuns; gera o estado inicial uma vez só |
| `comum/saida.py` | impressão no mesmo formato do professor |
| `comum/estatisticas.py` | melhoria: CSVs por geração e por *worker* |
| `comum/visualizacao.py` | melhoria: animação HTML |

Decisões principais:
- **Grade em `bytearray`** de (L+2)·C bytes, 1 byte por célula, com uma linha de zeros em cima e
  embaixo (moldura). A moldura faz o papel da borda fixa do professor e, na distribuída, do *halo*.
  As colunas continuam com teste de limite.
- **Buffer duplo**: a grade atual só é lida e a nova só é escrita; entre gerações troca-se a
  referência, sem `deepcopy`.
- **Estado inicial gerado uma vez** (processo principal ou coordenador) com a própria `criar_grade`
  do professor, semente 42. Nenhum *worker* sorteia nada, por isso as três versões dão o mesmo
  resultado.
- Cada *worker* conta os estados da sua faixa e o principal soma (redução).
- Mesmos parâmetros e padrões em todas as versões (100×100, 50 gerações, 5%, limiar 3).

## 2. Versão paralela

`python -m paralelo.fakenews_paralelo --trabalhadores N [--modo processos|threads]`
- Faixas horizontais contíguas (tamanhos diferem no máximo em 1 linha).
- **Processos** (padrão, método *spawn*): as duas grades em `multiprocessing.shared_memory`.
- **Threads**: o mesmo laço com `bytearray`; serve para o experimento que mostra o efeito do GIL.
- **Duas barreiras por geração** (modelo BSP): A, depois de calcular e contar; o principal soma,
  imprime e decide se continua; B, os *workers* esperam a decisão; depois todos trocam os buffers.
- Sem condição de corrida: cada *worker* escreve só as suas linhas e a sua posição de `contagens`.
- Timeout de 600 s nas barreiras (uma barreira presa vira erro em vez de travar).

## 3. Versão distribuída

`distribuido/`: `coordenador.py`, `worker.py`, `protocolo.py`, `executar_local.py`.
- **Protocolo**: cabeçalho de 5 bytes (tipo 1 B + tamanho 4 B *big-endian*) e leitura até completar
  a mensagem. Mensagens: OLA, INICIO, GRADE, LIMIARES, PRONTO, LARGADA, HALO, CONTAGEM, FAIXA,
  DECISAO, RESULTADO.
- O **coordenador** gera a grade, envia as faixas, soma as contagens e decide a parada.
- Os **workers trocam as bordas direto entre si** (em cadeia), em ordem par/ímpar para não haver
  *deadlock*.
- Host e porta por argumento, timeout em toda espera; `executar_local` sobe tudo numa máquina.
- Mais *workers* que linhas é recusado.

## 4. Testes

`python -m unittest discover -s testes -v`
- `test_modelo.py`: núcleo igual ao professor (grades aleatórias, bordas, várias gerações, faixas
  calculadas separadamente = grade inteira), conversões, borda em bits, melhorias do modelo.
- `test_equivalencia.py`: refatorada, paralela (processos e threads) e distribuída **iguais ao
  professor geração a geração**; com as melhorias ligadas, iguais à sequencial refatorada.
- `test_protocolo.py`: mensagens grandes e vazias, JSON, conexão fechada no meio, tipo errado.

## 5. Melhorias escolhidas

Cada melhoria vale até 0,5 ponto (máximo 3). No relatório, cada uma precisa de **motivação,
implementação, fundamentação (referência) e resultado**.

| # | Melhoria | Tipo | Como usar | Implementação | Referência candidata ([`final.md`](final.md)) |
|---|---|---|---|---|---|
| 1 | Grade compacta sem `deepcopy` | desempenho | sempre ligada | `comum/modelo.py`: vetor de bytes + moldura + buffer duplo | Giordano et al. (2019) |
| 2 | Estatísticas e perfil de tempo | instrumentação | `--estatisticas PASTA` | `comum/estatisticas.py`: CSV por geração e por *worker* (cálculo, comunicação, espera) | a definir |
| 3 | Visualização gráfica | apresentação | `--animacao grade.html` | `comum/visualizacao.py` | a definir |
| 4 | Resistência individual | modelo | `--resistencia MIN MAX` | limiar por célula sorteado com `Random(semente + 1)` | Jin et al. (2013); Amaral e Arenzon (2018) |
| 5 | *Bots* | modelo | `--bots 0.01` | estado `BOT = 3`: espalha sempre e nunca fica inativo; posições com `Random(semente + 2)` | Shao et al. (2018) |
| 6 | Borda compactada em bits | comunicação | `--bits` (distribuída) | `empacotar_bits`/`desempacotar_bits`: 1 bit por célula no *halo* (8× menor) | Giordano et al. (2019) |

As melhorias do modelo (4 e 5) ficam desligadas por padrão para reproduzir o professor; ligadas, as
três versões continuam iguais entre si (testado).

**Reservas** (têm artigo em [`final.md`](final.md), não implementadas): várias *fake news*
concorrentes (Shao et al., 2024), checadores de fatos (Tambuscio et al., 2015), influenciadores
(Kitsak et al., 2010), balanceamento dinâmico de carga (Giordano et al., 2021).

---

## 6. O que falta (ordem sugerida)

Esta lista acompanha o [roadmap do grupo](https://claude.ai/artifact/X6U3gNTZ2FdzgZEkaNCkkC),
onde cada um marca as suas tarefas.

0. [ ] **Confirmar o prazo de entrega e o número do grupo** (o número vai no nome do vídeo).
1. [ ] **Abrir o PR** de `feat/implementacoes-codigo` para a `main` e conseguir 1 aprovação.
   - [ ] revisar se todo o código está comentado em português;
   - [ ] conferir se o README tem as instruções de execução das três versões (Windows e Linux).
2. [ ] **Script de experimentos** em Python (`experimentos/`). Hoje o código já mede o tempo do
   laço (`tempo_laco`) e o tempo total com criação de processos/conexões (`tempo_total`), e já
   aceita os parâmetros de cada cenário; falta o script que roda tudo e calcula as métricas:
   - [ ] variar tamanho da grade, gerações, % de espalhadores, nº de *threads*/processos e nº de
     *workers*/hosts, com limiar 2;
   - [ ] rodar **os mesmos cenários nas três versões** (sequencial, paralela e distribuída);
   - [ ] 1 execução de aquecimento descartada + pelo menos 5 repetições, reportando a mediana;
   - [ ] gravar no CSV a **configuração da máquina**: processador, núcleos físicos e lógicos, RAM,
     sistema operacional, versão do Python e ambiente (notebook na tomada, local ou rede);
   - [ ] calcular **speedup** (S = T_seq / T_p) e **eficiência** (E = S / p) contra a sequencial,
     usando `tempo_laco` e também `tempo_total` (mostra o custo de subir processos/conexões);
   - [ ] (opcional) fração serial de **Karp–Flatt**, para diagnosticar sobrecarga e
     desbalanceamento.
3. [ ] **Medir as melhorias de desempenho**: grade compacta × original (`deepcopy`) e `--bits` ×
   1 byte por célula (tempo de comunicação pelo perfil por *worker*).
4. [ ] **Medir o efeito das melhorias do modelo**: espalhadores por geração com e sem resistência e
   *bots* (`--estatisticas`).
5. [ ] **Tabelas e gráficos** gerados por script, nunca editados à mão: tabela comparativa de
   tempos das três versões, gráfico de tempo, de *speedup* e de eficiência (paralela e
   distribuída), e cálculo × comunicação × espera por *worker*.
6. [ ] **Análises pedidas no enunciado** (subseções de "Análise" no capítulo de experimentos). Os
   dados já são coletados com `--estatisticas`; falta rodar e interpretar:
   - [ ] **gargalos**: tempo de cálculo por *worker* e índice de desbalanceamento (mais lento /
     média);
   - [ ] **sincronização**: `espera_s` (tempo nas barreiras da paralela e esperando a decisão do
     coordenador na distribuída);
   - [ ] **custo de comunicação**: `comunicacao_s` e `bytes_enviados` (só na distribuída; a
     paralela usa memória compartilhada), com e sem `--bits`;
   - [ ] **limitações observadas** (GIL no modo *threads*, núcleos P e E do processador, grade
     pequena demais para compensar a comunicação etc.).
7. [ ] **Relatório no Overleaf**. `\todo` pendentes (cópia de 23 nov.): introdução 1 · fundamentação 3
   · sequencial 2 · paralela 4 · distribuída 5 · melhorias 5 (faltam as 6 subseções) ·
   experimentos 13 · conclusão 6 · apêndice de execução 2. No capítulo de experimentos: preencher
   a tabela de ambiente (`tab:ambiente`), descrever os cenários e as repetições, e colocar as
   tabelas, os gráficos e as análises dos itens 5 e 6 (hoje só a fundamentação tem as fórmulas
   de *speedup*, eficiência, Amdahl e Gustafson). Na conclusão, a tabela de contribuições com os
   quatro integrantes; no apêndice, o registro do uso de IA. Cada seção é revisada por quem fez
   aquela parte do código.
8. [ ] **Referências** das melhorias 2 e 3 e do uso de IA (o enunciado exige citar).
9. [ ] **Slides** em PDF:
   - [ ] todos os tópicos do enunciado: problema, modelo, sequencial, paralela e distribuída,
     divisão da matriz, tabelas e gráficos, *speedup* e eficiência, dificuldades, melhorias,
     referências;
   - [ ] contribuição individual de cada integrante;
   - [ ] registro do uso de IA, de código externo e de bibliotecas;
   - [ ] exportar em PDF.
10. [ ] **Vídeo** de 10–15 min com todos:
    - [ ] roteiro em que cada integrante explica uma parte do código (decisões, divisão do
      processamento, sincronização e comunicação, quem fez o quê);
    - [ ] demonstrar a paralela e a distribuída funcionando e a análise dos resultados;
    - [ ] gravar com todos de câmera ligada (quem não aparece fica com zero);
    - [ ] conferir o formato: MP4, H.264 1280×720 a 30 fps, AAC estéreo 44,1 kHz, sem marca
      d'água, edição só para cortar (cada erro de formato tira 0,5);
    - [ ] nome do arquivo `AAAA-MM-DD - Grupo XX - FakeNews.mp4`.
11. [ ] Rodar paralela e distribuída também no **Linux** e, se possível, a distribuída entre 2 ou
    mais máquinas reais.
12. [ ] **Entrega**:
    - [ ] montar o **ZIP** com código, instruções, PDF dos slides e vídeo (ou link na nuvem
      acessível até o fim da avaliação);
    - [ ] enviar no **Moodle** antes do prazo (atraso não é aceito).

---

## Histórico

- **23 nov. 2026**: arquivo criado. Três versões, 6 melhorias e testes na branch
  `feat/implementacoes-codigo` (no GitHub, ainda sem PR). Relatório sincronizado com a fundamentação
  e as referências. Nenhum experimento rodado.
- **23 nov. 2026**: checklist detalhada com as métricas e análises de desempenho pedidas no
  enunciado e alinhada ao roadmap do grupo (slides, vídeo e entrega).
