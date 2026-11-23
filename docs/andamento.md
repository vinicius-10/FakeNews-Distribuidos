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
| Distribuída (sockets TCP) | ✅ feita e testada (localhost, interface de rede real e 3 máquinas) | [`distribuido/`](../distribuido/) |
| Testes | ✅ 56 testes passando (Windows e Linux): equivalência, protocolo, robustez, melhorias 2 e 3, saída, métricas | [`testes/`](../testes/) |
| 6 melhorias | ✅ implementadas · ✅ medidas · ❌ não escritas no relatório | [seção 5](#5-melhorias-escolhidas) |
| Experimentos de desempenho | ✅ medidos numa máquina (localhost) · 🔄 3 máquinas: conexão ok, falta medir | [`experimentos/`](../experimentos/) |
| Relatório (Overleaf) | 🔄 fundamentação e seção 3 (sequencial) escritas; o resto tem `\todo` | [`relatorio/`](../relatorio/) (cópia) |
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
- `test_robustez.py`: na distribuída, conexões que não são *workers* (fecha logo, HTTP, tipo
  errado, JSON/UTF-8 inválido, sem `porta_halo`, silenciosa) são descartadas e o resultado continua
  igual ao do professor; `tempo_total` sem a espera pelos *workers*; *worker* que cai ou trava vira
  `ErroProtocolo` citando a geração, sem travar.
- `test_melhorias_saida.py`: estatísticas e animação ligadas não mudam a grade em nenhuma versão;
  contagens por geração iguais às do professor; perfil por *worker*; CSVs e HTML gravados certos;
  `resumo()` e amostragem da animação com números feitos à mão.
- `test_saida.py`: texto impresso pela refatorada igual ao do professor (com e sem a grade);
  paralela e distribuída imprimem as mesmas gerações e o mesmo resultado.
- `test_metricas.py`: *speedup*, eficiência, Karp–Flatt, Amdahl, Gustafson, mediana/desvio e
  conferência dos hashes, com valores calculados à mão.

Suíte inteira: ~15 s no Windows e ~5 s no Linux (WSL).

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
1. [x] **Código na `main`**:
   - [x] PR [#3](https://github.com/vinicius-10/FakeNews-Distribuidos/pull/3) (três versões, 6
     melhorias e testes): aprovado e integrado em 23 nov.;
   - [x] PR [#4](https://github.com/vinicius-10/FakeNews-Distribuidos/pull/4) (experimentos e
     robustez): integrado na `feat/implementacoes-codigo` em 23 nov.;
   - [x] PR [#5](https://github.com/vinicius-10/FakeNews-Distribuidos/pull/5) de
     `feat/implementacoes-codigo` para a `main` (leva o PR #4): aprovado e integrado em 23 nov.;
   - [x] PRs #6 a #9 (roteiro das 3 máquinas, scripts de rede, testes completos e custo da
     sequencial) integrados em 23 nov.;
   - [ ] apagar as branches já integradas que ficaram no GitHub (`docs/andamento-3-maquinas`,
     `docs/guia-contribuicao`, `docs/referencias`, `feat/experimentos-custo-sequencial`,
     `feat/experimentos-e-robustez`, `feat/implementacoes-codigo`, `fix/scripts-rede-notebooks`,
     `test/completar-testes`).
2. [x] **Script de experimentos** em Python ([`experimentos/`](../experimentos/README.md)):
   `medir.py` (baterias), `analisar.py` (métricas, tabelas e gráficos), `perfis.py` (tempo por
   *worker*) e `modelo.py` (melhorias do modelo).
   - [x] variar tamanho da grade (500², 1000², 2000²) e nº de processos/*threads*/*workers*
     (1 a 24), com limiar 2;
   - [ ] variar **gerações** e **% de espalhadores** (o `medir.py` já aceita `--geracoes` e
     `--percentual`; as baterias usaram só 20 gerações e 5%). 🔄 Em andamento na branch
     `feat/bateria-parametros` (Rafael, ainda sem PR): bateria que varia percentual e limiar nas
     três versões; gerações ainda não;
   - [x] rodar **os mesmos cenários nas três versões**; o SHA-256 da grade final confirma que
     todas deram o mesmo resultado em todas as execuções;
   - [x] 1 execução de aquecimento descartada + repetições, reportando a mediana (5 ou mais na
     paralela e na distribuída; 3 na do professor, que é a mais lenta);
   - [x] gravar a **configuração da máquina** em `resultados/ambiente.csv` (i9-12900F, 16 núcleos
     físicos / 24 lógicos, 31,8 GB, Windows, Python 3.11.7, desktop na tomada);
   - [x] calcular **speedup** e **eficiência** sobre `tempo_laco` e `tempo_total`;
   - [x] fração serial de **Karp–Flatt**, limite de Amdahl e Gustafson.
3. [x] **Medir as melhorias de desempenho** (`resultados/tabelas.md`, `perfis.md`):
   - grade compacta × original (`deepcopy`): **3,3× a 3,5×** mais rápida com 1 trabalhador;
   - `--bits`: *halo* de ~1.921 para ~281 bytes por *worker* por geração (16 *workers*, 1000²),
     sem ganho de tempo em `localhost` (o ganho só aparece numa rede real).
4. [x] **Medir o efeito das melhorias do modelo** (`resultados/modelo.md`): resistência 1–3
   aumenta o alcance em +17 p.p.; resistência 3–5 derruba para 5%; *bots* 2% levam a 93%.
   - [x] **custo da sequencial do professor** (`resultados/custo_sequencial.md`, script
     `custo_sequencial.py`): varredura 75%, `deepcopy` 21% e contagem 4% do tempo de uma
     geração; célula ignorante ~1,02 µs contra ~0,06 µs dos outros estados; limiar ×
     percentual em 1000×1000; memória de 8,9 bytes por célula (lista de listas) contra 1,04
     (vetor de bytes). Medido no i7-13650HX; usado na seção 3.4 do relatório.
5. [x] **Tabelas e gráficos** gerados por script (`resultados/tabelas.md` e
   `resultados/graficos/`: *speedup*, eficiência, GIL, melhorias e modelo).
6. [ ] **Análises pedidas no enunciado**: os dados estão medidos; falta escrever a interpretação
   no capítulo de experimentos:
   - [x] **gargalos**: desbalanceamento de 1,00 a 1,10 (mais lento / média);
   - [x] **sincronização**: a espera nas barreiras sobe de 0,05% (1 *worker*) para ~19%
     (16 *workers*) do laço;
   - [x] **custo de comunicação**: abaixo de 2,5% do laço em `localhost`, com e sem `--bits`;
   - [x] **limitações**: GIL (modo *threads* sem ganho: speedup de 0,87 a 0,97 com 1 a 24 *threads*),
     eficiência caindo acima de 8 *workers* (núcleos P/E) e speedup superlinear com 2 *workers*
     (cache);
   - [ ] texto das análises no relatório (item 7).
7. [ ] **Relatório no Overleaf**. `\todo` pendentes (cópia de 23 nov., commit `139cd2b`):
   introdução 1 · paralela 4 · distribuída 5 · melhorias 5 (faltam as 6 subseções) ·
   experimentos 13 · conclusão 6 · apêndice de execução 2. Fundamentação e seção 3 (sequencial:
   funcionamento com fluxograma e exemplo passo a passo, e análise de custo) estão completas. No capítulo de experimentos (ou no
   apêndice), um parágrafo sobre a verificação: os 56 testes, o que cada grupo cobre e a
   conferência por SHA-256 nas baterias; no da distribuída, o descarte de conexões que não são
   *workers*, os *timeouts* e o que o `tempo_total` mede. No capítulo de experimentos: preencher
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
11. [ ] Rodar em outros ambientes:
    - [x] **Linux**: testes e as três versões rodados no Ubuntu (WSL, Python 3.12.3), com o mesmo
      resultado do Windows;
    - [x] **Linux nativo** (Fedora, i5-1240P, `main` em `ec05145`, depois do PR #9): 56 testes OK
      com Python 3.12.16 e 3.14.10 (~5,5 s); `custo_sequencial --rapido` OK; em 400×400, 30
      gerações e limiar 2, sequencial, paralela (8 processos e 4 *threads*) e distribuída
      (4 *workers*, com e sem `--bits`) deram 67.670 / 54 / 92.276;
    - [x] **interface de rede real**: distribuída com `--host 0.0.0.0` e *workers* conectando
      pelo IP da máquina (2 e 3 *workers*), mesmo resultado da sequencial
      ([`validacao.md`](../experimentos/resultados/rede/validacao.md));
    - [x] a distribuída **entre 3 máquinas reais** funcionando (roteiro em
      [`distribuido/rede/LEIA-ME-3-maquinas.md`](../distribuido/rede/LEIA-ME-3-maquinas.md)):
      rede privada e *firewall* liberados nas 3; 200×200, limiar 2, 3 *workers* (um por máquina)
      deu o mesmo resultado da sequencial (17.027 ignorantes e 22.973 inativos na geração 44).
      Tempo do laço 1,07 s, contra 0,36 s da sequencial: com grade pequena a rede domina
      (~24 ms por geração);
    - [ ] **medir** entre 3 máquinas: 2000×2000 com repetições, 1 *worker* por máquina, com e sem
      `--bits`, 2 *workers* por máquina, e os mesmos 3 *workers* em `localhost` para comparar
      (custo da rede real);
    - [x] coordenador: o `tempo_total` começa depois que o último *worker* conecta (antes
      incluía a espera, 100,9 s no teste) e uma conexão que não é *worker* (ex.:
      `Test-NetConnection` na porta 5000) é descartada em vez de derrubar o coordenador
      (`test_robustez.py`);
    - [x] scripts `.ps1`/`.sh` de `distribuido/rede/` mantidos como auxiliares do teste entre
      máquinas (*firewall*, pacote, preparo dos notebooks); a simulação continua com `python -m`.
      O `preparar-no-linux.sh` baixa a `main` por padrão.
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
- **23 nov. 2026**: PR #3 aberto; código revisado (comentários em português, README completo).
  Testes e as três versões rodados no Linux (Ubuntu no WSL), iguais ao Windows: 27 testes passando
  e, em 400×400 com limiar 2, a mesma contagem final em todas as versões. Experimentos passaram
  para outro integrante.
- **23 nov. 2026**: PR #3 integrado na `main`. PR #4 (experimentos e correções de robustez)
  integrado na `feat/implementacoes-codigo`: baterias em 500², 1000² e 2000² com 1 a 24
  *workers*, perfil por *worker*, efeito das melhorias e validação da distribuída pela interface
  de rede. Speedup do laço em 2000² com 24 *workers*: 10,9 (paralela) e 12,2 (distribuída em
  `localhost`). PR #5 aberto para levar tudo à `main`.
- **23 nov. 2026**: PR #5 integrado; o código e os experimentos estão todos na `main`. Distribuída
  rodada entre 3 máquinas reais na rede local (teste de conexão em 200×200, mesmo resultado da
  sequencial). Falta medir em 2000×2000 e corrigir no coordenador o `tempo_total` e o descarte de
  conexões que não são *workers*.
- **23 nov. 2026**: scripts de `distribuido/rede/` mantidos como auxiliares opcionais; agora
  descrevem notebooks (não TV box) e o `preparar-no-linux.sh` baixa a `main` por padrão.
- **23 nov. 2026**: testes completados (27 → 56) e coordenador corrigido. Conexões que não são
  *workers* são descartadas (espera de até 10 s pelo OLA) e o `tempo_total` da distribuída começa
  depois que todos os *workers* conectam; os CSVs antigos da distribuída têm `tempo_total` com a
  subida dos processos, o `tempo_laco` não mudou. A grade impressa com `--mostrar-grade` ficou
  idêntica à do professor (espaço no fim da linha).
- **23 nov. 2026**: seção 3 do relatório escrita (3.3 funcionamento da sequencial, com fluxograma e
  exemplo 5×5 passo a passo; 3.4 análise de custo). Novo `experimentos/custo_sequencial.py` mede o
  custo do código do professor (perfil por etapa, custo por estado, limiar × percentual e memória).
- **23 nov. 2026**: `main` depois do PR #9 conferida em Linux nativo (Fedora, i5-1240P): 56 testes
  OK com Python 3.12 e 3.14 e as três versões com o mesmo resultado. Registrados a bateria de
  percentual e limiar em andamento (`feat/bateria-parametros`) e as branches integradas que
  ainda podem ser apagadas.
