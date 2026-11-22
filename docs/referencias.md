# 📚 Referências do trabalho

Artigos, livros e documentação técnica que fundamentam o modelo, a arquitetura das versões
paralela e distribuída e a análise de desempenho. Cada entrada traz a referência no formato
ABNT (NBR 6023:2018), os dados de publicação, o link, um resumo e onde ela entra no trabalho.

> **Como os dados foram conferidos (22/11/2026):** autores, datas, volumes e páginas vêm do
> registro oficial do DOI na [Crossref](https://www.crossref.org/), da página do arXiv ou do
> catálogo da editora. A linha **Lido** de cada entrada diz de onde saiu o resumo (resumo oficial,
> texto completo ou só os metadados). Antes de citar uma afirmação específica no relatório, leia o
> trecho correspondente no texto original.

## 📑 Sumário

| # | Referência | Tema | No `main.bib` |
|---|---|---|---|
| 1 | [Daley e Kendall (1964)](#1-daley-e-kendall-1964--epidemics-and-rumours) | Modelo de rumor | `DaleyKendall1964` |
| 2 | [Coletti, Rodríguez e Schinazi (2012)](#2-coletti-rodríguez-e-schinazi-2012--a-spatial-stochastic-model-for-rumor-transmission) | Rumor em reticulado | — |
| 3 | [Granovetter (1978)](#3-granovetter-1978--threshold-models-of-collective-behavior) | Modelo de limiar | `Granovetter1978` |
| 4 | [Vosoughi, Roy e Aral (2018)](#4-vosoughi-roy-e-aral-2018--the-spread-of-true-and-false-news-online) | *Fake news* (motivação) | `Vosoughi2018` |
| 5 | [Wolfram (1983)](#5-wolfram-1983--statistical-mechanics-of-cellular-automata) | Autômatos celulares | `Wolfram1983` |
| 6 | [Bandini, Mauri e Serra (2001)](#6-bandini-mauri-e-serra-2001--cellular-automata-from-a-theoretical-parallel-computational-model-to-its-application-to-complex-systems) | AC como modelo paralelo | — |
| 7 | [Foster (1995)](#7-foster-1995--designing-and-building-parallel-programs) | Metodologia PCAM | — |
| 8 | [Mattson, Sanders e Massingill (2004)](#8-mattson-sanders-e-massingill-2004--patterns-for-parallel-programming) | Padrões de programação paralela | — |
| 9 | [Valiant (1990)](#9-valiant-1990--a-bridging-model-for-parallel-computation) | Modelo BSP | — |
| 10 | [Kjolstad e Snir (2010)](#10-kjolstad-e-snir-2010--ghost-cell-pattern) | Células fantasmas (*halo*) | — |
| 11 | [Ding e He (2001)](#11-ding-e-he-2001--a-ghost-cell-expansion-method-for-reducing-communications-in-solving-pde-problems) | *Halo* largo (melhoria) | — |
| 12 | [Bourached (2017)](#12-bourached-2017--blocking-versus-non-blocking-halo-exchange) | Troca de *halo* bloqueante × não bloqueante | — |
| 13 | [Xia et al. (2025)](#13-xia-et-al-2025--dynamic-load-balancing-based-on-hypergraph-partitioning-for-parallel-geospatial-cellular-automata-models) | Balanceamento dinâmico (melhoria) | — |
| 14 | [Amdahl (1967)](#14-amdahl-1967--validity-of-the-single-processor-approach-to-achieving-large-scale-computing-capabilities) | Lei de Amdahl | `Amdahl1967` |
| 15 | [Gustafson (1988)](#15-gustafson-1988--reevaluating-amdahls-law) | Lei de Gustafson | `Gustafson1988` |
| 16 | [Pacheco (2011)](#16-pacheco-2011--an-introduction-to-parallel-programming) | Livro-texto: programação paralela | `Pacheco2011` |
| 17 | [Van Steen e Tanenbaum (2017)](#17-van-steen-e-tanenbaum-2017--distributed-systems) | Livro-texto: sistemas distribuídos | `Tanenbaum2017` |
| 18 | [Gross (2023), PEP 703](#18-gross-2023--pep-703-making-the-global-interpreter-lock-optional-in-cpython) | GIL do Python | — |
| 19 | [Python Software Foundation, `shared_memory`](#19-python-software-foundation--multiprocessingshared_memory-python-312) | Memória compartilhada | — |

---

## 🧠 Modelo de propagação

### 1. Daley e Kendall (1964) — *Epidemics and rumours*

- **Autores:** D. J. Daley; D. G. Kendall
- **Publicado em:** *Nature*, v. 204, n. 4963, p. 1118, 12 dez. 1964
- **DOI:** [10.1038/2041118a0](https://doi.org/10.1038/2041118a0)
- **ABNT:** DALEY, D. J.; KENDALL, D. G. Epidemics and rumours. *Nature*, [*s. l.*], v. 204,
  n. 4963, p. 1118, 1964. DOI: 10.1038/2041118a0.
- **Resumo:** carta curta em que os autores tratam a difusão de um boato com as ferramentas da
  epidemiologia matemática, respondendo a Goffman e Newill, que tinham apontado a analogia entre
  a propagação de doenças e a de informação. A população é dividida em quem não conhece o boato,
  quem o espalha e quem deixou de espalhar. A diferença para as epidemias é o fim da propagação:
  quem espalha para de espalhar ao encontrar alguém que já conhece o boato. Os autores observam que
  nem os resultados qualitativos precisam seguir a analogia com as epidemias. O trabalho completo
  saiu depois como *Stochastic rumours* (*J. Inst. Math. Appl.*, 1965). É a origem do chamado
  modelo de Daley–Kendall.
- **No trabalho:** origem dos três estados da simulação (ignorante, espalhador, inativo). Seção
  de fundamentação.
- **Lido:** metadados (Crossref) e descrições da carta em páginas que a citam; o texto da *Nature*
  exige login.

### 2. Coletti, Rodríguez e Schinazi (2012) — *A spatial stochastic model for rumor transmission*

- **Autores:** Cristian F. Coletti; Pablo M. Rodríguez; Rinaldo B. Schinazi
- **Publicado em:** *Journal of Statistical Physics*, v. 147, n. 2, p. 375–381, abr. 2012
  (pré-publicação no arXiv em 17 fev. 2012)
- **DOI:** [10.1007/s10955-012-0469-y](https://doi.org/10.1007/s10955-012-0469-y) ·
  arXiv: [1202.4019](https://arxiv.org/abs/1202.4019)
- **ABNT:** COLETTI, C. F.; RODRÍGUEZ, P. M.; SCHINAZI, R. B. A spatial stochastic model for
  rumor transmission. *Journal of Statistical Physics*, [*s. l.*], v. 147, n. 2, p. 375–381,
  2012. DOI: 10.1007/s10955-012-0469-y.
- **Resumo:** estuda um sistema de partículas interagentes que modela a propagação de um boato
  entre agentes no reticulado inteiro de dimensão *d*. Cada agente está em um de três estados:
  0 (ignorante), 1 (espalhador) e 2 (abafador). Um espalhador transmite o boato aos vizinhos
  ignorantes mais próximos com taxa λ e vira abafador com taxa α por causa de espalhadores
  vizinhos; espalhadores e abafadores esquecem o boato com taxa 1. O resultado principal são
  condições suficientes para o boato se extinguir ou sobreviver com probabilidade positiva.
- **No trabalho:** mostra que o modelo de rumor com três estados também é estudado numa grade com
  vizinhança local, como a da simulação. Também serve de base para uma melhoria probabilística
  (convencimento com probabilidade).
- **Lido:** resumo oficial (arXiv) e metadados (Crossref).

### 3. Granovetter (1978) — *Threshold models of collective behavior*

- **Autor:** Mark Granovetter
- **Publicado em:** *American Journal of Sociology*, v. 83, n. 6, p. 1420–1443, maio 1978
- **DOI:** [10.1086/226707](https://doi.org/10.1086/226707)
- **ABNT:** GRANOVETTER, M. Threshold models of collective behavior. *American Journal of
  Sociology*, [*s. l.*], v. 83, n. 6, p. 1420–1443, 1978. DOI: 10.1086/226707.
- **Resumo:** propõe os modelos de limiar para o comportamento coletivo: cada indivíduo adota um
  comportamento quando o número (ou a proporção) de outros que já o adotaram atinge o seu limiar
  pessoal. Pequenas diferenças na distribuição dos limiares podem levar a resultados coletivos
  muito diferentes.
- **No trabalho:** fundamenta o **limiar de convencimento** da simulação: o ignorante vira
  espalhador com pelo menos `limiar` vizinhos espalhadores.
- **Lido:** metadados (Crossref); resumo pelo conteúdo amplamente conhecido do artigo, **a
  conferir no texto** antes de citar detalhes.

### 4. Vosoughi, Roy e Aral (2018) — *The spread of true and false news online*

- **Autores:** Soroush Vosoughi; Deb Roy; Sinan Aral
- **Publicado em:** *Science*, v. 359, n. 6380, p. 1146–1151, 9 mar. 2018
- **DOI:** [10.1126/science.aap9559](https://doi.org/10.1126/science.aap9559)
- **ABNT:** VOSOUGHI, S.; ROY, D.; ARAL, S. The spread of true and false news online. *Science*,
  [*s. l.*], v. 359, n. 6380, p. 1146–1151, 2018. DOI: 10.1126/science.aap9559.
- **Resumo:** analisa cascatas de boatos no Twitter de 2006 a 2017, cerca de 126 mil boatos
  espalhados por cerca de 3 milhões de pessoas. A notícia falsa alcançou mais gente que a
  verdadeira: o 1% maior das cascatas falsas chegou a entre 1.000 e 100.000 pessoas, enquanto a
  verdade raramente passou de 1.000. A falsidade também se espalhou mais rápido. A novidade e as
  reações emocionais de quem recebe podem explicar a diferença.
- **No trabalho:** motivação da introdução (relevância de simular *fake news*).
- **Lido:** resumo editorial oficial (Crossref).

---

## 🔲 Autômatos celulares

### 5. Wolfram (1983) — *Statistical mechanics of cellular automata*

- **Autor:** Stephen Wolfram
- **Publicado em:** *Reviews of Modern Physics*, v. 55, n. 3, p. 601–644, 1 jul. 1983
- **DOI:** [10.1103/RevModPhys.55.601](https://doi.org/10.1103/RevModPhys.55.601)
- **ABNT:** WOLFRAM, S. Statistical mechanics of cellular automata. *Reviews of Modern Physics*,
  [*s. l.*], v. 55, n. 3, p. 601–644, 1983. DOI: 10.1103/RevModPhys.55.601.
- **Resumo:** estudo clássico de autômatos celulares como sistemas dinâmicos discretos: grades de
  células com estados finitos, atualizadas em paralelo e em passos discretos por uma regra local.
  Analisa o comportamento estatístico de autômatos simples e mostra que regras locais simples
  podem gerar comportamento global complexo.
- **No trabalho:** definição de autômato celular na fundamentação.
- **Lido:** metadados (Crossref); resumo pelo conteúdo amplamente conhecido, **a conferir no
  texto**.

### 6. Bandini, Mauri e Serra (2001) — *Cellular automata: from a theoretical parallel computational model to its application to complex systems*

- **Autores:** S. Bandini; G. Mauri; R. Serra (a Crossref registra só as iniciais; conferir os
  nomes completos no artigo)
- **Publicado em:** *Parallel Computing*, v. 27, n. 5, p. 539–553, abr. 2001
- **DOI:** [10.1016/S0167-8191(00)00076-4](https://doi.org/10.1016/S0167-8191(00)00076-4) ·
  repositório: [BOA Unimib](https://boa.unimib.it/handle/10281/3183)
- **ABNT:** BANDINI, S.; MAURI, G.; SERRA, R. Cellular automata: from a theoretical parallel
  computational model to its application to complex systems. *Parallel Computing*, [*s. l.*],
  v. 27, n. 5, p. 539–553, 2001. DOI: 10.1016/S0167-8191(00)00076-4.
- **Resumo:** levantamento introdutório em três partes: (1) definições e teoria dos autômatos
  celulares como modelo abstrato de computação e como sistemas dinâmicos discretos; (2) uso do
  modelo para representar sistemas complexos em áreas como biologia e física; (3) implementações
  do modelo em plataformas de computação paralela.
- **No trabalho:** justifica tratar o autômato celular como um problema naturalmente paralelo
  (regra local, atualização simultânea) na fundamentação.
- **Lido:** metadados (Crossref) e descrição do resumo no repositório institucional (a página
  bloqueia acesso automático; ler o texto pelo DOI).

---

## ⚙️ Projeto de programas paralelos

### 7. Foster (1995) — *Designing and building parallel programs*

- **Autor:** Ian Foster
- **Publicado por:** Addison-Wesley, 1995, xiii + 381 p., ISBN 0-201-57594-9
- **Link:** [versão online do livro](https://www.mcs.anl.gov/~itf/dbpp/) (gratuita para leitura)
- **ABNT:** FOSTER, I. *Designing and building parallel programs*: concepts and tools for
  parallel software engineering. [*S. l.*]: Addison-Wesley, 1995. Disponível em:
  https://www.mcs.anl.gov/~itf/dbpp/. Acesso em: 22 nov. 2026.
- **Resumo:** trata a programação paralela como engenharia: o programa é projetado de forma
  metódica, considerando custo e desempenho em cada etapa. O capítulo 2 apresenta a metodologia
  **PCAM**: **particionamento** (dividir dados e cálculo em tarefas pequenas), **comunicação**
  (definir o que as tarefas precisam trocar), **aglomeração** (juntar tarefas para aumentar a
  granularidade, a razão entre cálculo e comunicação) e **mapeamento** (atribuir as tarefas aos
  processadores, de forma estática ou dinâmica).
- **No trabalho:** roteiro da decisão de dividir a grade em faixas de linhas contíguas (cada
  faixa é uma aglomeração de linhas; só as linhas da borda precisam ser comunicadas).
- **Lido:** catálogos de bibliotecas (dados do livro) e páginas de curso que resumem o PCAM; o
  site do livro bloqueia acesso automático.

### 8. Mattson, Sanders e Massingill (2004) — *Patterns for parallel programming*

- **Autores:** Timothy G. Mattson; Beverly A. Sanders; Berna L. Massingill
- **Publicado por:** Addison-Wesley, 2004 (assim citado pelos próprios autores; há catálogos que
  registram a impressão de 2005, ISBN 0-321-22811-1)
- **Link:** [site do projeto *Parallel Patterns*](https://www.cise.ufl.edu/research/ParallelPatterns/) ·
  [artigo PLoP 2005 que resume a linguagem de padrões](https://www.cise.ufl.edu/research/ParallelPatterns/plop2005.pdf)
- **ABNT:** MATTSON, T. G.; SANDERS, B. A.; MASSINGILL, B. L. *Patterns for parallel
  programming*. [*S. l.*]: Addison-Wesley, 2004.
- **Resumo:** linguagem de padrões para desenvolver programas paralelos, organizada em quatro
  espaços de projeto: encontrar a concorrência, estrutura do algoritmo, estruturas de suporte e
  mecanismos de implementação. Os padrões usados aqui são: **Geometric Decomposition** ("como
  organizar um algoritmo em torno de uma estrutura de dados decomposta em pedaços que podem ser
  atualizados ao mesmo tempo?"), **SPMD** (um mesmo programa em todas as unidades de execução,
  para tornar as interações entre elas mais fáceis de gerenciar) e **Master/Worker** (quando é
  preciso balancear a carga dinamicamente).
- **No trabalho:** a decomposição em faixas é uma *Geometric Decomposition*; os *workers*
  executam o mesmo código sobre faixas diferentes (SPMD); o padrão alerta para *deadlock* na troca
  de bordas, motivo da ordem par/ímpar na versão distribuída.
- **Lido:** texto do artigo PLoP 2005 dos mesmos autores (descrição dos padrões e referência do
  livro); o livro não foi lido.

### 9. Valiant (1990) — *A bridging model for parallel computation*

- **Autor:** Leslie G. Valiant
- **Publicado em:** *Communications of the ACM*, v. 33, n. 8, p. 103–111, ago. 1990
- **DOI:** [10.1145/79173.79181](https://doi.org/10.1145/79173.79181)
- **ABNT:** VALIANT, L. G. A bridging model for parallel computation. *Communications of the ACM*,
  New York, v. 33, n. 8, p. 103–111, 1990. DOI: 10.1145/79173.79181.
- **Resumo:** argumenta que o modelo de von Neumann deu certo porque é uma ponte eficiente entre
  *software* e *hardware*, e que a computação paralela precisa de uma ponte análoga. Propõe o
  modelo **BSP** (*bulk-synchronous parallel*): o programa avança em *supersteps*; em cada um, os
  processadores calculam localmente e trocam mensagens, e uma sincronização em barreira encerra o
  *superstep*. O artigo quantifica a eficiência do modelo tanto para implementar linguagens e
  algoritmos quanto para ser implementado em *hardware*.
- **No trabalho:** cada geração da simulação é um *superstep*: calcular a faixa → barreira →
  redução das contagens → decisão de parar.
- **Lido:** resumo oficial (Crossref) e resenha do artigo em
  [*the morning paper*](https://blog.acolyer.org/2015/06/08/a-bridging-model-for-parallel-computation/).

---

## 🧱 Troca de bordas (*halo*)

### 10. Kjolstad e Snir (2010) — *Ghost cell pattern*

- **Autores:** Fredrik Berg Kjolstad; Marc Snir (University of Illinois at Urbana-Champaign)
- **Publicado em:** *2nd Annual Conference on Parallel Programming Patterns* (ParaPLoP '10),
  Carefree, AZ, 30–31 mar. 2010
- **Link:** [PDF](https://edoras.sdsu.edu/~mthomas/f17.705/topics/iter_solv/gropp_iter_solv/kjoldtad_snir_2010_ghostcell.pdf)
- **ABNT:** KJOLSTAD, F. B.; SNIR, M. Ghost cell pattern. *In*: ANNUAL CONFERENCE ON PARALLEL
  PROGRAMMING PATTERNS, 2., 2010, Carefree. *Proceedings* […]. [*S. l.*: *s. n.*], 2010.
- **Resumo:** muitos problemas são grades estruturadas atualizadas repetidamente a partir de
  vizinhos fixos (estênceis). Ao dividir a grade em pedaços entre processadores, as células da
  periferia de cada pedaço precisam de valores dos pedaços vizinhos, muitas vezes em memória
  remota, e a implementação ingênua gasta muito tempo em comunicação. **Solução:** reservar
  células fantasmas em volta de cada pedaço e, a cada iteração, cada par de vizinhos troca uma
  cópia das bordas e a guarda nessa região (o *halo*), que não é atualizada localmente e só
  fornece valores para o estêncil. Variações: **Deep Halo** (*halo* mais largo para trocar menos
  vezes, pagando com cálculo redundante, porque a latência de cada mensagem costuma superar o
  tempo de transmissão), **Corner Cells** (estêncil com vizinhos diagonais), troca assíncrona e
  sobreposição de comunicação com cálculo.
- **No trabalho:** base da versão distribuída: cada *worker* guarda sua faixa mais 1 linha de
  *halo* em cima e embaixo. Com faixas de linhas inteiras, os vizinhos diagonais (Moore) já vêm
  nas linhas trocadas, sem troca extra de cantos.
- **Lido:** texto completo (resumo, problema, solução e seções 5.1 a 5.4).

### 11. Ding e He (2001) — *A ghost cell expansion method for reducing communications in solving PDE problems*

- **Autores:** Chris H. Q. Ding; Yun He (NERSC, Lawrence Berkeley National Laboratory)
- **Publicado em:** SC2001 (*ACM/IEEE Conference on Supercomputing*), Denver, nov. 2001;
  também relatório técnico LBNL-47929 (maio 2001)
- **Link:** [eScholarship](https://escholarship.org/uc/item/5wz950tp) ·
  [OSTI](https://www.osti.gov/biblio/783770)
- **ABNT:** DING, C. H. Q.; HE, Y. A ghost cell expansion method for reducing communications in
  solving PDE problems. *In*: ACM/IEEE CONFERENCE ON SUPERCOMPUTING, 2001, Denver.
  *Proceedings* […]. New York: ACM, 2001.
- **Resumo:** em solucionadores de EDP por diferenças finitas em domínios regulares, a troca de
  células fantasmas a cada passo domina a comunicação. O método **expande** a camada de células
  fantasmas para *e* camadas extras, de modo que as mensagens são trocadas a cada *e*+1 passos em
  vez de a cada passo: o volume total cai e mensagens pequenas viram mensagens maiores, ao custo de
  um pouco mais de memória e de cálculo. Combinado com a eliminação das comunicações diagonais, o
  método acelera a comunicação em até 170%, com medições no Cray T3E e no IBM SP.
- **No trabalho:** **melhoria candidata** "redução de comunicação distribuída": *halo* de *k*
  linhas trocado a cada *k* gerações.
- **Lido:** resumo do registro OSTI/eScholarship (via busca); a página do eScholarship não abriu
  por acesso automático.

### 12. Bourached (2017) — *Blocking versus non-blocking halo exchange*

- **Autor:** Anthony Bourached (MSc in High Performance Computing, The University of Edinburgh,
  trabalho apresentado em 2016)
- **Publicado em:** arXiv, 18 set. 2017 (cs.DC)
- **Link:** [arXiv:1709.06175](https://arxiv.org/abs/1709.06175)
- **ABNT:** BOURACHED, A. *Blocking versus non-blocking halo exchange*. [*S. l.*]: arXiv, 2017.
  DOI: 10.48550/arXiv.1709.06175.
- **Resumo:** projeta, implementa e analisa uma rotina de troca de *halo* **não bloqueante** como
  alternativa à rotina bloqueante do código de *lattice Boltzmann* Ludwig. A versão não
  bloqueante foi feita para permitir sobrepor trabalho e comunicação. Os *benchmarks* mostram que
  ela já é uma boa alternativa mesmo sem sobreposição, e que a sobreposição pode melhorar ainda
  mais o desempenho. Desenvolvimento e medições no supercomputador ARCHER (Reino Unido).
- **No trabalho:** justifica começar pela troca bloqueante (simples de explicar) e deixar a
  sobreposição de comunicação e cálculo como **melhoria candidata**.
- **Lido:** resumo oficial (arXiv).

---

## ⚖️ Balanceamento de carga

### 13. Xia et al. (2025) — *Dynamic load balancing based on hypergraph partitioning for parallel geospatial cellular automata models*

- **Autores:** Wei Xia; Qingfeng Guan; Yuanyuan Li; Hanqiu Yue; Xue Yang; Huan Gao
- **Publicado em:** *ISPRS International Journal of Geo-Information*, v. 14, n. 3, art. 109,
  mar. 2025 (MDPI)
- **DOI:** [10.3390/ijgi14030109](https://doi.org/10.3390/ijgi14030109)
- **ABNT:** XIA, W. *et al*. Dynamic load balancing based on hypergraph partitioning for
  parallel geospatial cellular automata models. *ISPRS International Journal of
  Geo-Information*, [*s. l.*], v. 14, n. 3, p. 109, 2025. DOI: 10.3390/ijgi14030109.
- **Resumo:** em autômatos celulares geoespaciais paralelos (mudança de uso e cobertura do solo),
  a distribuição do custo de cálculo muda ao longo da simulação, desbalanceando os processos. O
  artigo redistribui os subdomínios dinamicamente por particionamento de hipergrafos conforme a
  carga observada e propõe o mecanismo MSCF (*Migrated-SubCellspaces-First*), que usa comunicação
  não bloqueante para reduzir o custo de migrar carga. Com dados da Califórnia, o balanceamento
  dinâmico melhorou o desempenho em **62,59% com 16 processos** em relação ao balanceamento
  estático.
- **No trabalho:** **melhoria candidata** "balanceamento dinâmico de carga". Na nossa simulação
  só os ignorantes contam vizinhos, então faixas com mais ignorantes custam mais.
- **Lido:** resumo oficial (Crossref); a página da MDPI bloqueia acesso automático.

---

## 📈 Métricas de desempenho

### 14. Amdahl (1967) — *Validity of the single processor approach to achieving large scale computing capabilities*

- **Autor:** Gene M. Amdahl
- **Publicado em:** *AFIPS Spring Joint Computer Conference* (AFIPS '67), Atlantic City,
  18–20 abr. 1967, p. 483–485
- **DOI:** [10.1145/1465482.1465560](https://doi.org/10.1145/1465482.1465560)
- **ABNT:** AMDAHL, G. M. Validity of the single processor approach to achieving large scale
  computing capabilities. *In*: AFIPS SPRING JOINT COMPUTER CONFERENCE, 1967, Atlantic City.
  *Proceedings* […]. New York: ACM, 1967. p. 483–485. DOI: 10.1145/1465482.1465560.
- **Resumo:** argumento que deu origem à **lei de Amdahl**: a parte do programa que não pode ser
  paralelizada limita o *speedup* máximo, por mais processadores que se usem.
- **No trabalho:** análise dos experimentos (parte serial: criar a grade, distribuir as faixas,
  redução e decisão de parada a cada geração).
- **Lido:** metadados (Crossref); resumo pelo conteúdo amplamente conhecido, **a conferir no
  texto**.

### 15. Gustafson (1988) — *Reevaluating Amdahl's law*

- **Autor:** John L. Gustafson
- **Publicado em:** *Communications of the ACM*, v. 31, n. 5, p. 532–533, maio 1988
- **DOI:** [10.1145/42411.42415](https://doi.org/10.1145/42411.42415)
- **ABNT:** GUSTAFSON, J. L. Reevaluating Amdahl's law. *Communications of the ACM*, New York,
  v. 31, n. 5, p. 532–533, 1988. DOI: 10.1145/42411.42415.
- **Resumo:** propõe o ***speedup* escalado** (lei de Gustafson): quando o tamanho do problema
  cresce junto com o número de processadores, a fração serial perde peso e o *speedup* pode
  crescer quase linearmente.
- **No trabalho:** experimentos de escalabilidade fraca (grade maior com mais processos).
- **Lido:** metadados (Crossref); resumo pelo conteúdo amplamente conhecido, **a conferir no
  texto**.

---

## 📘 Livros-texto da disciplina

### 16. Pacheco (2011) — *An introduction to parallel programming*

- **Autor:** Peter S. Pacheco
- **Publicado por:** Morgan Kaufmann, Boston, 2011, 392 p., ISBN 978-0-12-374260-5
  (2.ª edição, com Matthew Malensek, em 2021: ISBN 978-0-12-804605-0)
- **Link:** [Elsevier](https://shop.elsevier.com/books/an-introduction-to-parallel-programming/pacheco/978-0-12-374260-5)
- **ABNT:** PACHECO, P. S. *An introduction to parallel programming*. Boston: Morgan
  Kaufmann, 2011. (O `main.bib` registra Burlington; os catálogos consultados dizem Boston.)
- **Resumo:** livro-texto que ensina a projetar, depurar e avaliar o desempenho de programas
  paralelos em memória distribuída (MPI) e compartilhada (Pthreads, OpenMP).
- **No trabalho:** definições de *speedup* e eficiência; memória compartilhada × troca de
  mensagens; barreiras.
- **Lido:** catálogo da editora e de bibliotecas.

### 17. Van Steen e Tanenbaum (2017) — *Distributed systems*

- **Autores:** Maarten van Steen; Andrew S. Tanenbaum
- **Publicado por:** CreateSpace (publicação independente), 3. ed., versão 3.01, fev. 2017,
  596 p., ISBN 978-1-5430-5738-6
- **Link:** [distributed-systems.net](https://www.distributed-systems.net/index.php/books/distributed-systems-3rd-edition-2017/)
  (PDF gratuito)
- **ABNT:** VAN STEEN, M.; TANENBAUM, A. S. *Distributed systems*. 3. ed. [*S. l.*]: CreateSpace,
  2017.
- **Resumo:** livro-texto de sistemas distribuídos em nove capítulos: introdução, arquiteturas,
  processos, comunicação, nomeação, coordenação, consistência e replicação, tolerância a falhas e
  segurança.
- **No trabalho:** arquitetura coordenador–*workers*, comunicação por *sockets* e sincronização na
  versão distribuída.
- **Lido:** catálogos e páginas dos autores. **Atenção:** a ordem oficial dos autores é van Steen
  e Tanenbaum; a entrada `Tanenbaum2017` do `main.bib` está invertida.

---

## 🐍 Python

### 18. Gross (2023) — PEP 703: *Making the Global Interpreter Lock optional in CPython*

- **Autor:** Sam Gross (patrocinador: Łukasz Langa)
- **Publicado em:** *Python Enhancement Proposals*, criada em 9 jan. 2023; status *Final*
  (aceita em 24 out. 2023), alvo: Python 3.13
- **Link:** [peps.python.org/pep-0703](https://peps.python.org/pep-0703/)
- **ABNT:** GROSS, S. *PEP 703*: making the global interpreter lock optional in CPython.
  [*S. l.*]: Python Software Foundation, 2023. Disponível em: https://peps.python.org/pep-0703/.
  Acesso em: 22 nov. 2026.
- **Resumo:** o GIL (*Global Interpreter Lock*) impede que várias *threads* executem código
  Python ao mesmo tempo, o que dificulta usar CPUs com vários núcleos. A PEP propõe uma opção de
  compilação do CPython (`--disable-gil`) para rodar sem o GIL. A motivação relata que as
  alternativas atuais, como o `multiprocessing`, têm custos de comunicação entre processos,
  serialização e memória.
- **No trabalho:** explica por que, no Python 3.12 usado pelo grupo, `threading` não acelera o
  cálculo e a versão paralela usa processos.
- **Lido:** texto da PEP (cabeçalho, *Abstract* e *Motivation*).

### 19. Python Software Foundation — `multiprocessing.shared_memory` (Python 3.12)

- **Autor:** Python Software Foundation
- **Publicado em:** documentação oficial do Python 3.12 (módulo criado no Python 3.8)
- **Link:** [docs.python.org/3.12/library/multiprocessing.shared_memory.html](https://docs.python.org/3.12/library/multiprocessing.shared_memory.html)
- **ABNT:** PYTHON SOFTWARE FOUNDATION. *multiprocessing.shared_memory*: shared memory for direct
  access across processes. Python 3.12 documentation. [*S. l.*], [20--] (ano a conferir). Disponível em:
  https://docs.python.org/3.12/library/multiprocessing.shared_memory.html. Acesso em:
  22 nov. 2026.
- **Resumo:** a classe `SharedMemory` cria blocos de memória compartilhada acessíveis por vários
  processos da mesma máquina (não é memória compartilhada distribuída). Cada bloco tem um nome, e
  outro processo se conecta a ele por esse nome; o atributo `buf` dá acesso aos bytes. Todo
  processo chama `close()` quando não precisa mais do bloco, e `unlink()` deve ser chamado **uma
  única vez** entre todos os processos. O comportamento da destruição pode variar entre
  plataformas, e o tamanho pode ser arredondado para cima (por exemplo, para uma página de
  memória).
- **No trabalho:** a versão paralela guarda as duas grades (atual e próxima) em blocos
  `SharedMemory`, lidos e escritos pelos processos *workers* sem cópia.
- **Lido:** documentação completa da página.

---

## ✍️ Como acrescentar uma referência

1. Confira os dados no registro do DOI (`https://doi.org/<doi>`) ou no catálogo da editora.
2. Acrescente a entrada aqui, na seção do tema, com a linha **Lido** dizendo o que foi lido.
3. Acrescente a entrada BibTeX no `main.bib` do Overleaf (nunca alterar as que já existem) e cite
   no texto com `\cite{chave}` ou `\citeonline{chave}`.
