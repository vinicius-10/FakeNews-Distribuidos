# 📚 Referências do trabalho

Artigos, livros e documentação técnica que fundamentam o modelo, a arquitetura das versões
paralela e distribuída e a análise de desempenho. **Só entram fontes de acesso aberto:** qualquer
pessoa abre e baixa o texto completo, sem login institucional e sem pagar.

Cada entrada traz: autores, data, onde foi publicada, o link para o **texto completo**, a
referência no formato ABNT (NBR 6023:2018), um resumo, onde ela entra no trabalho e o que foi lido
para escrever o resumo.

> **Como os dados foram conferidos (22/11/2026):** autores, datas, volumes e páginas vêm do
> registro oficial do DOI na [Crossref](https://www.crossref.org/), da página do arXiv, do
> Zenodo ou da própria página da obra. O acesso aberto foi conferido no
> [OpenAlex](https://openalex.org/) e na própria fonte. Antes de citar uma afirmação específica no
> relatório, leia o trecho correspondente no texto original.

## 📑 Sumário

| # | Referência | Tema | Texto completo |
|---|---|---|---|
| 1 | [Moreno, Nekovee e Pacheco (2004)](#1-moreno-nekovee-e-pacheco-2004--dynamics-of-rumor-spreading-in-complex-networks) | Modelo de rumor | arXiv |
| 2 | [Nekovee et al. (2007)](#2-nekovee-et-al-2007--theory-of-rumour-spreading-in-complex-social-networks) | Modelo de rumor | arXiv |
| 3 | [Coletti, Rodríguez e Schinazi (2012)](#3-coletti-rodríguez-e-schinazi-2012--a-spatial-stochastic-model-for-rumor-transmission) | Rumor em reticulado | arXiv |
| 4 | [Watts (2002)](#4-watts-2002--a-simple-model-of-global-cascades-on-random-networks) | Regra de limiar | PubMed Central |
| 5 | [Del Vicario et al. (2016)](#5-del-vicario-et-al-2016--the-spreading-of-misinformation-online) | Desinformação (motivação) | PubMed Central |
| 6 | [Berto e Tagliabue (2012, rev. 2023)](#6-berto-e-tagliabue-2012-rev-2023--cellular-automata) | Autômatos celulares | Stanford Encyclopedia of Philosophy |
| 7 | [Marzolla (2018)](#7-marzolla-2018--parallel-implementations-of-cellular-automata-for-traffic-models) | AC paralelos | arXiv |
| 8 | [Foster (1995)](#8-foster-1995--designing-and-building-parallel-programs) | Metodologia PCAM | site do livro |
| 9 | [Massingill, Mattson e Sanders (2005)](#9-massingill-mattson-e-sanders-2005--reengineering-for-parallelism) | Padrões de programação paralela | site dos autores (UF) |
| 10 | [Valiant (1990)](#10-valiant-1990--a-bridging-model-for-parallel-computation) | Modelo BSP | ACM Digital Library |
| 11 | [Eijkhout, Chow e van de Geijn (2016)](#11-eijkhout-chow-e-van-de-geijn-2016--introduction-to-high-performance-scientific-computing) | Livro-texto de PAD (CC BY) | Zenodo |
| 12 | [Kjolstad e Snir (2010)](#12-kjolstad-e-snir-2010--ghost-cell-pattern) | Células fantasmas (*halo*) | PDF em página de disciplina |
| 13 | [Ding e He (2001)](#13-ding-e-he-2001--a-ghost-cell-expansion-method-for-reducing-communications-in-solving-pde-problems) | *Halo* largo (melhoria) | OSTI |
| 14 | [Bourached (2017)](#14-bourached-2017--blocking-versus-non-blocking-halo-exchange) | Troca de *halo* bloqueante × não bloqueante | arXiv |
| 15 | [Xia et al. (2025)](#15-xia-et-al-2025--dynamic-load-balancing-based-on-hypergraph-partitioning-for-parallel-geospatial-cellular-automata-models) | Balanceamento dinâmico (melhoria) | MDPI (CC BY) |
| 16 | [Amdahl (1967)](#16-amdahl-1967--validity-of-the-single-processor-approach-to-achieving-large-scale-computing-capabilities) | Lei de Amdahl | PDF em página de disciplina |
| 17 | [Gustafson (1988)](#17-gustafson-1988--reevaluating-amdahls-law) | Lei de Gustafson | ACM Digital Library |
| 18 | [Van Steen e Tanenbaum (2023)](#18-van-steen-e-tanenbaum-2023--distributed-systems) | Livro-texto de sistemas distribuídos | site dos autores (cópia gratuita) |
| 19 | [Gross (2023), PEP 703](#19-gross-2023--pep-703-making-the-global-interpreter-lock-optional-in-cpython) | GIL do Python | peps.python.org |
| 20 | [Python: glossário, *global interpreter lock*](#20-python-software-foundation--glossário-global-interpreter-lock-python-312) | GIL do Python | docs.python.org |
| 21 | [Python: `multiprocessing.shared_memory`](#21-python-software-foundation--multiprocessingshared_memory-python-312) | Memória compartilhada | docs.python.org |

Fontes retiradas por não terem texto aberto: [ver o fim do arquivo](#-retiradas-por-não-serem-de-acesso-aberto).

---

## 🧠 Modelo de propagação

### 1. Moreno, Nekovee e Pacheco (2004) — *Dynamics of rumor spreading in complex networks*

- **Autores:** Yamir Moreno; Maziar Nekovee; Amalio F. Pacheco
- **Publicado em:** *Physical Review E*, v. 69, n. 6, art. 066130, 17 jun. 2004 (pré-publicação
  no arXiv em 4 dez. 2003)
- **Texto completo:** [arXiv:cond-mat/0312131](https://arxiv.org/abs/cond-mat/0312131) ·
  [PDF](https://arxiv.org/pdf/cond-mat/0312131)
- **DOI:** [10.1103/PhysRevE.69.066130](https://doi.org/10.1103/PhysRevE.69.066130)
- **ABNT:** MORENO, Y.; NEKOVEE, M.; PACHECO, A. F. Dynamics of rumor spreading in complex
  networks. *Physical Review E*, [*s. l.*], v. 69, n. 6, p. 066130, 2004.
  DOI: 10.1103/PhysRevE.69.066130. Disponível em: https://arxiv.org/abs/cond-mat/0312131.
  Acesso em: 22 nov. 2026.
- **Resumo:** deduz as equações de campo médio da dinâmica de um processo de rumor sobre redes
  complexas heterogêneas e as resolve numericamente por uma abordagem estocástica. Primeiro
  compara cálculos analíticos e de Monte Carlo em redes homogêneas com o método numérico; depois
  estuda em detalhe o espalhamento em redes livres de escala aleatórias. Os perfis no tempo de
  várias grandezas permitem distinguir variantes de algoritmos de espalhamento de rumores. As
  conclusões apontam aplicações em manutenção de bancos de dados replicados, redes *peer-to-peer*
  e fenômenos de espalhamento social.
- **No trabalho:** fundamentação do modelo de três estados (ignorante, espalhador, abafador/inativo)
  que vem da tradição de Daley–Kendall e Maki–Thompson.
- **Lido:** resumo oficial (arXiv) e metadados (Crossref).

### 2. Nekovee et al. (2007) — *Theory of rumour spreading in complex social networks*

- **Autores:** Maziar Nekovee; Yamir Moreno; Ginestra Bianconi; Matteo Marsili
- **Publicado em:** *Physica A*, v. 374, n. 1, p. 457–470, jan. 2007 (versão no arXiv em
  9 jul. 2008)
- **Texto completo:** [arXiv:0807.1458](https://arxiv.org/abs/0807.1458) ·
  [PDF](https://arxiv.org/pdf/0807.1458)
- **DOI:** [10.1016/j.physa.2006.07.017](https://doi.org/10.1016/j.physa.2006.07.017)
- **ABNT:** NEKOVEE, M. *et al*. Theory of rumour spreading in complex social networks.
  *Physica A*, [*s. l.*], v. 374, n. 1, p. 457–470, 2007. DOI: 10.1016/j.physa.2006.07.017.
  Disponível em: https://arxiv.org/abs/0807.1458. Acesso em: 22 nov. 2026.
- **Resumo:** propõe um modelo estocástico geral de espalhamento de rumores e deduz as equações
  de campo médio da sua dinâmica em redes sociais complexas, em especial as mediadas pela
  Internet. Em redes homogêneas e grafos aleatórios, o modelo tem um limiar crítico na taxa de
  espalhamento, abaixo do qual o rumor não se propaga; em redes livres de escala esse limiar tende
  a zero quando o sistema cresce. O rumor se espalha bem mais rápido no início em redes livres de
  escala, e mais ainda com correlações assortativas de grau. Conclui que redes sociais livres de
  escala são propensas ao espalhamento de rumores, como são ao de infecções.
- **No trabalho:** fundamentação do modelo e da existência de um limiar para a propagação; apoio a
  melhorias do modelo (redes/grafos, influenciadores).
- **Lido:** resumo oficial (arXiv) e metadados (Crossref).

### 3. Coletti, Rodríguez e Schinazi (2012) — *A spatial stochastic model for rumor transmission*

- **Autores:** Cristian F. Coletti; Pablo M. Rodríguez; Rinaldo B. Schinazi
- **Publicado em:** *Journal of Statistical Physics*, v. 147, n. 2, p. 375–381, abr. 2012
  (pré-publicação no arXiv em 17 fev. 2012)
- **Texto completo:** [arXiv:1202.4019](https://arxiv.org/abs/1202.4019) ·
  [PDF](https://arxiv.org/pdf/1202.4019)
- **DOI:** [10.1007/s10955-012-0469-y](https://doi.org/10.1007/s10955-012-0469-y)
- **ABNT:** COLETTI, C. F.; RODRÍGUEZ, P. M.; SCHINAZI, R. B. A spatial stochastic model for
  rumor transmission. *Journal of Statistical Physics*, [*s. l.*], v. 147, n. 2, p. 375–381,
  2012. DOI: 10.1007/s10955-012-0469-y. Disponível em: https://arxiv.org/abs/1202.4019. Acesso
  em: 22 nov. 2026.
- **Resumo:** estuda um sistema de partículas interagentes que modela a propagação de um rumor
  entre agentes no reticulado inteiro de dimensão *d*. Cada agente está em um de três estados:
  0 (ignorante), 1 (espalhador) e 2 (abafador). Um espalhador transmite o rumor aos vizinhos
  ignorantes mais próximos com taxa λ e vira abafador com taxa α por causa de espalhadores
  vizinhos; espalhadores e abafadores esquecem o rumor com taxa 1. O resultado principal são
  condições suficientes para o rumor se extinguir ou sobreviver com probabilidade positiva.
- **No trabalho:** mostra que o modelo de rumor de três estados também é estudado numa grade com
  vizinhança local, como a da simulação; base para uma melhoria probabilística.
- **Lido:** resumo oficial (arXiv) e metadados (Crossref).

### 4. Watts (2002) — *A simple model of global cascades on random networks*

- **Autor:** Duncan J. Watts
- **Publicado em:** *Proceedings of the National Academy of Sciences* (PNAS), v. 99, n. 9,
  p. 5766–5771, 30 abr. 2002
- **Texto completo:** [PubMed Central PMC122850](https://pmc.ncbi.nlm.nih.gov/articles/PMC122850/)
- **DOI:** [10.1073/pnas.082090499](https://doi.org/10.1073/pnas.082090499)
- **ABNT:** WATTS, D. J. A simple model of global cascades on random networks. *Proceedings of
  the National Academy of Sciences*, Washington, v. 99, n. 9, p. 5766–5771, 2002.
  DOI: 10.1073/pnas.082090499. Disponível em: https://pmc.ncbi.nlm.nih.gov/articles/PMC122850/.
  Acesso em: 22 nov. 2026.
- **Resumo:** explica cascatas grandes e raras, disparadas por choques iniciais pequenos (modismos,
  ação coletiva, difusão de inovações, falhas em cascata), com uma rede aleatória esparsa de
  agentes cujas decisões seguem uma **regra de limiar simples** sobre as ações dos vizinhos.
  Identifica dois regimes em que a rede é suscetível a cascatas globais. Quando a propagação é
  limitada pela conectividade, o tamanho das cascatas segue uma lei de potência; quando a rede é
  muito conectada, a propagação é limitada pela estabilidade local dos nós e a distribuição é
  bimodal. A heterogeneidade tem papel ambíguo na estabilidade do sistema.
- **No trabalho:** fundamenta o **limiar de convencimento** (o ignorante vira espalhador com pelo
  menos `limiar` vizinhos espalhadores).
- **Lido:** resumo oficial (Crossref).

### 5. Del Vicario et al. (2016) — *The spreading of misinformation online*

- **Autores:** Michela Del Vicario; Alessandro Bessi; Fabiana Zollo; Fabio Petroni; Antonio
  Scala; Guido Caldarelli; H. Eugene Stanley; Walter Quattrociocchi
- **Publicado em:** *PNAS*, v. 113, n. 3, p. 554–559, 19 jan. 2016
- **Texto completo:** [PubMed Central PMC4725489](https://pmc.ncbi.nlm.nih.gov/articles/PMC4725489/)
- **DOI:** [10.1073/pnas.1517441113](https://doi.org/10.1073/pnas.1517441113)
- **ABNT:** DEL VICARIO, M. *et al*. The spreading of misinformation online. *Proceedings of the
  National Academy of Sciences*, Washington, v. 113, n. 3, p. 554–559, 2016.
  DOI: 10.1073/pnas.1517441113. Disponível em:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC4725489/. Acesso em: 22 nov. 2026.
- **Resumo:** com uma análise quantitativa massiva do Facebook, mostra que informações ligadas a
  narrativas distintas (teorias da conspiração e notícias científicas) formam comunidades
  homogêneas e polarizadas, as câmaras de eco, com padrões de consumo semelhantes. Os autores
  derivam um modelo de percolação de espalhamento de rumores, baseado nos dados, que mostra que
  homogeneidade e polarização são os principais determinantes do tamanho das cascatas.
- **No trabalho:** motivação da introdução (relevância de simular a propagação de desinformação).
- **Lido:** resumo oficial (*Significance*, Crossref).

---

## 🔲 Autômatos celulares

### 6. Berto e Tagliabue (2012, rev. 2023) — *Cellular automata*

- **Autores:** Francesco Berto; Jacopo Tagliabue
- **Publicado em:** *The Stanford Encyclopedia of Philosophy*, Stanford University. Primeira
  publicação em 26 mar. 2012; revisão substantiva em 15 dez. 2023
- **Texto completo:** [plato.stanford.edu/entries/cellular-automata](https://plato.stanford.edu/entries/cellular-automata/)
- **ABNT:** BERTO, F.; TAGLIABUE, J. Cellular automata. *In*: ZALTA, E. N.; NODELMAN, U. (ed.).
  *The Stanford Encyclopedia of Philosophy*. Stanford: Stanford University, 2023. Disponível em:
  https://plato.stanford.edu/entries/cellular-automata/. Acesso em: 22 nov. 2026.
- **Resumo:** verbete acadêmico revisado por pares. Define autômatos celulares como sistemas
  computacionais abstratos e discretos, discretos no espaço e no tempo, formados por um conjunto
  finito ou enumerável de células idênticas, cada uma num estado de um conjunto finito. As células
  são atualizadas em paralelo, em passos discretos, por uma função de transição local que depende
  só da vizinhança, sem ação a distância. A seção 2.1 lista os quatro elementos de um AC: reticulado
  discreto de *n* dimensões, estados discretos, interações locais por vizinhança e dinâmica discreta
  por uma função de transição determinística, normalmente síncrona.
- **No trabalho:** definição de autômato celular, vizinhança e atualização síncrona na
  fundamentação.
- **Lido:** texto do verbete (seção 2.1 e datas). **Conferir** a linha de autoria na página e os
  editores da edição consultada antes de citar.

### 7. Marzolla (2018) — *Parallel implementations of cellular automata for traffic models*

- **Autor:** Moreno Marzolla
- **Publicado em:** MAURI, G. *et al*. (ed.). *Cellular Automata*: ACRI 2018. Lecture Notes in
  Computer Science, v. 11115. Springer, 2018 (pré-publicação no arXiv em 21 abr. 2018)
- **Texto completo:** [arXiv:1804.07981](https://arxiv.org/abs/1804.07981) ·
  [PDF](https://arxiv.org/pdf/1804.07981)
- **ABNT:** MARZOLLA, M. Parallel implementations of cellular automata for traffic models.
  *In*: INTERNATIONAL CONFERENCE ON CELLULAR AUTOMATA FOR RESEARCH AND INDUSTRY, 13., 2018.
  *Cellular Automata*. Cham: Springer, 2018. (Lecture Notes in Computer Science, v. 11115).
  Disponível em: https://arxiv.org/abs/1804.07981. Acesso em: 22 nov. 2026.
- **Resumo:** usa o modelo de tráfego Biham–Middleton–Levine, um autômato celular 2D discreto
  cujas células mudam de estado por regras simples que dependem delas e dos vizinhos, como estudo
  de caso de otimizações para acelerar AC. Descreve e analisa implementações paralelas com vários
  núcleos, instruções SIMD e GPU, medindo o *speedup* de cada técnica em relação à versão serial
  simples. Conclui que a diferença de desempenho entre CPU e GPU pode ser reduzida aproveitando bem
  todos os recursos da CPU.
- **No trabalho:** exemplo de paralelização de um AC 2D com medição de *speedup*, comparável à nossa
  análise experimental.
- **Lido:** resumo oficial (arXiv).

---

## ⚙️ Projeto de programas paralelos

### 8. Foster (1995) — *Designing and building parallel programs*

- **Autor:** Ian Foster
- **Publicado por:** Addison-Wesley, 1995, xiii + 381 p., ISBN 0-201-57594-9. O autor mantém o
  texto completo gratuito na Internet
- **Texto completo:** [mcs.anl.gov/~itf/dbpp](https://www.mcs.anl.gov/~itf/dbpp/) (capítulo 2:
  [metodologia](https://www.mcs.anl.gov/~itf/dbpp/text/node15.html))
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
  faixa aglomera linhas; só as linhas da borda precisam ser comunicadas).
- **Lido:** catálogos de bibliotecas (dados do livro) e páginas de curso que resumem o PCAM; o site
  do livro abre no navegador, mas recusa acesso automático.

### 9. Massingill, Mattson e Sanders (2005) — *Reengineering for parallelism*

- **Título completo:** *Reengineering for parallelism: an entry point into PLPP (Pattern Language
  for Parallel Programming) for legacy applications*
- **Autores:** Berna L. Massingill (Trinity University); Timothy G. Mattson (Intel); Beverly A.
  Sanders (University of Florida)
- **Publicado em:** *Pattern Languages of Programs* (PLoP 2005)
- **Texto completo:** [PDF no site do projeto *Parallel Patterns*](https://www.cise.ufl.edu/research/ParallelPatterns/plop2005.pdf)
- **ABNT:** MASSINGILL, B. L.; MATTSON, T. G.; SANDERS, B. A. Reengineering for parallelism: an
  entry point into PLPP (Pattern Language for Parallel Programming) for legacy applications.
  *In*: CONFERENCE ON PATTERN LANGUAGES OF PROGRAMS, 12., 2005. *Proceedings* […]. [*S. l.*:
  *s. n.*], 2005. Disponível em:
  https://www.cise.ufl.edu/research/ParallelPatterns/plop2005.pdf. Acesso em: 22 nov. 2026.
- **Resumo:** os autores desenvolveram uma linguagem de padrões para programas paralelos (PLPP),
  publicada em livro em 2004, que parte do entendimento do problema e passa por uma sequência de
  padrões até chegar ao código. Este artigo trata do caso mais comum na prática: **paralelizar um
  código sequencial já existente**, e dá um ponto de entrada na linguagem para esse caso. O artigo
  também resume os padrões da PLPP, entre eles **Geometric Decomposition** ("como organizar um
  algoritmo em torno de uma estrutura de dados decomposta em pedaços que podem ser atualizados ao
  mesmo tempo?"), **SPMD** (estruturar o programa para que as interações entre as unidades de
  execução fiquem mais fáceis de gerenciar) e **Master/Worker** (quando é preciso balancear a carga
  dinamicamente).
- **No trabalho:** é exatamente a nossa situação (paralelizar o código sequencial do professor);
  a divisão em faixas é uma *Geometric Decomposition* e os *workers* executam o mesmo código sobre
  faixas diferentes (SPMD).
- **Lido:** texto do artigo (resumo, introdução e lista de padrões).

### 10. Valiant (1990) — *A bridging model for parallel computation*

- **Autor:** Leslie G. Valiant
- **Publicado em:** *Communications of the ACM*, v. 33, n. 8, p. 103–111, ago. 1990
- **Texto completo:** [ACM Digital Library (PDF)](https://dl.acm.org/doi/pdf/10.1145/79173.79181).
  A ACM liberou para leitura e *download* gratuitos tudo o que publicou de 1951 a 2000
  ([anúncio de abril de 2022](https://www.acm.org/media-center/2022/april/50-years-backfile))
- **DOI:** [10.1145/79173.79181](https://doi.org/10.1145/79173.79181)
- **ABNT:** VALIANT, L. G. A bridging model for parallel computation. *Communications of the ACM*,
  New York, v. 33, n. 8, p. 103–111, 1990. DOI: 10.1145/79173.79181.
- **Resumo:** argumenta que o modelo de von Neumann deu certo porque é uma ponte eficiente entre
  *software* e *hardware*, e que a computação paralela precisa de uma ponte análoga. Propõe o
  modelo **BSP** (*bulk-synchronous parallel*): o programa avança em *supersteps*; em cada um, os
  processadores calculam localmente e trocam mensagens, e uma sincronização em barreira encerra o
  *superstep*. Quantifica a eficiência do modelo tanto para implementar linguagens e algoritmos
  quanto para ser implementado em *hardware*.
- **No trabalho:** cada geração da simulação é um *superstep*: calcular a faixa → barreira →
  redução das contagens → decisão de parar.
- **Lido:** resumo oficial (Crossref) e resenha em
  [*the morning paper*](https://blog.acolyer.org/2015/06/08/a-bridging-model-for-parallel-computation/).

### 11. Eijkhout, Chow e van de Geijn (2016) — *Introduction to high performance scientific computing*

- **Autores:** Victor Eijkhout, com Edmond Chow e Robert van de Geijn
- **Publicado em:** 2. ed., revisão de 2016, Zenodo, 17 abr. 2016. Licença **Creative Commons
  BY** (o PDF diz CC BY 3.0; o registro do Zenodo, CC BY 4.0)
- **Texto completo:** [Zenodo (PDF)](https://zenodo.org/records/49897)
- **DOI:** [10.5281/zenodo.49897](https://doi.org/10.5281/zenodo.49897)
- **ABNT:** EIJKHOUT, V.; CHOW, E.; VAN DE GEIJN, R. *Introduction to high performance scientific
  computing*. 2. ed. [*S. l.*]: Zenodo, 2016. DOI: 10.5281/zenodo.49897.
- **Resumo:** livro-texto aberto de computação científica de alto desempenho (arquitetura,
  computação paralela, álgebra linear numérica, aplicações). As partes usadas aqui são: **seção
  2.2.1**, definições de *speedup* e eficiência; **seção 2.2.3**, lei de Amdahl (também com custo
  de comunicação) e lei de Gustafson; **seção 2.6.8**, modelo BSP (*supersteps* terminados por
  barreira, o que facilita a programação e elimina a possibilidade de *deadlock*); **seção
  6.5.2**, *ghost region* de um processador induzida por um estêncil e a diferença entre
  particionar o domínio em 1D e em 2D.
- **No trabalho:** substitui o livro-texto pago nas definições de *speedup*, eficiência, Amdahl,
  Gustafson, BSP e *ghost region*.
- **Lido:** registro do Zenodo e as seções citadas do PDF.

---

## 🧱 Troca de bordas (*halo*)

### 12. Kjolstad e Snir (2010) — *Ghost cell pattern*

- **Autores:** Fredrik Berg Kjolstad; Marc Snir (University of Illinois at Urbana-Champaign)
- **Publicado em:** *2nd Annual Conference on Parallel Programming Patterns* (ParaPLoP '10),
  Carefree, AZ, 30–31 mar. 2010
- **Texto completo:** [PDF](https://edoras.sdsu.edu/~mthomas/f17.705/topics/iter_solv/gropp_iter_solv/kjoldtad_snir_2010_ghostcell.pdf)
  (cópia pública numa página de disciplina da San Diego State University; não há cópia na editora)
- **ABNT:** KJOLSTAD, F. B.; SNIR, M. Ghost cell pattern. *In*: ANNUAL CONFERENCE ON PARALLEL
  PROGRAMMING PATTERNS, 2., 2010, Carefree. *Proceedings* […]. [*S. l.*: *s. n.*], 2010.
  Disponível em:
  https://edoras.sdsu.edu/~mthomas/f17.705/topics/iter_solv/gropp_iter_solv/kjoldtad_snir_2010_ghostcell.pdf.
  Acesso em: 22 nov. 2026.
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
- **No trabalho:** base da versão distribuída: cada *worker* guarda a sua faixa mais 1 linha de
  *halo* em cima e embaixo. Com faixas de linhas inteiras, os vizinhos diagonais (Moore) já vêm
  nas linhas trocadas, sem troca extra de cantos.
- **Lido:** texto completo (resumo, problema, solução e seções 5.1 a 5.4).

### 13. Ding e He (2001) — *A ghost cell expansion method for reducing communications in solving PDE problems*

- **Autores:** Chris H. Q. Ding; Yun He (NERSC, Lawrence Berkeley National Laboratory)
- **Publicado em:** SC2001 (*ACM/IEEE Conference on Supercomputing*), Denver, nov. 2001;
  relatório técnico LBNL-47929, maio 2001
- **Texto completo:** [OSTI (PDF)](https://www.osti.gov/servlets/purl/783770) ·
  [registro no OSTI](https://www.osti.gov/biblio/783770) (repositório do Departamento de Energia dos EUA)
- **ABNT:** DING, C. H. Q.; HE, Y. *A ghost cell expansion method for reducing communications in
  solving PDE problems*. Berkeley: Lawrence Berkeley National Laboratory, 2001. (Relatório
  LBNL-47929). Disponível em: https://www.osti.gov/biblio/783770. Acesso em: 22 nov. 2026.
- **Resumo:** em solucionadores de EDP por diferenças finitas em domínios regulares, a troca de
  células fantasmas a cada passo domina a comunicação. O método **expande** a camada de células
  fantasmas em *e* camadas extras, de modo que as mensagens são trocadas a cada *e*+1 passos em
  vez de a cada passo: o volume total cai e mensagens pequenas viram mensagens maiores, ao custo de
  um pouco mais de memória e de cálculo. Combinado com a eliminação das comunicações diagonais, o
  método acelera a comunicação em até 170%, com medições no Cray T3E e no IBM SP.
- **No trabalho:** **melhoria candidata** de redução de comunicação: *halo* de *k* linhas trocado a
  cada *k* gerações.
- **Lido:** resumo do registro OSTI e da cópia no eScholarship (via busca).

### 14. Bourached (2017) — *Blocking versus non-blocking halo exchange*

- **Autor:** Anthony Bourached (MSc in High Performance Computing, The University of Edinburgh,
  trabalho apresentado em 2016)
- **Publicado em:** arXiv, 18 set. 2017 (cs.DC)
- **Texto completo:** [arXiv:1709.06175](https://arxiv.org/abs/1709.06175) ·
  [PDF](https://arxiv.org/pdf/1709.06175)
- **ABNT:** BOURACHED, A. *Blocking versus non-blocking halo exchange*. [*S. l.*]: arXiv, 2017.
  DOI: 10.48550/arXiv.1709.06175.
- **Resumo:** projeta, implementa e analisa uma rotina de troca de *halo* **não bloqueante** como
  alternativa à rotina bloqueante do código de *lattice Boltzmann* Ludwig. A versão não bloqueante
  foi feita para permitir sobrepor trabalho e comunicação. Os *benchmarks* mostram que ela já é uma
  boa alternativa mesmo sem sobreposição, e que a sobreposição pode melhorar ainda mais o
  desempenho. Desenvolvimento e medições no supercomputador ARCHER (Reino Unido).
- **No trabalho:** justifica começar pela troca bloqueante (simples de explicar) e deixar a
  sobreposição de comunicação e cálculo como **melhoria candidata**.
- **Lido:** resumo oficial (arXiv).

---

## ⚖️ Balanceamento de carga

### 15. Xia et al. (2025) — *Dynamic load balancing based on hypergraph partitioning for parallel geospatial cellular automata models*

- **Autores:** Wei Xia; Qingfeng Guan; Yuanyuan Li; Hanqiu Yue; Xue Yang; Huan Gao
- **Publicado em:** *ISPRS International Journal of Geo-Information*, v. 14, n. 3, art. 109,
  1 mar. 2025 (MDPI, acesso aberto, licença CC BY)
- **Texto completo:** [MDPI](https://www.mdpi.com/2220-9964/14/3/109) ·
  [PDF](https://www.mdpi.com/2220-9964/14/3/109/pdf)
- **DOI:** [10.3390/ijgi14030109](https://doi.org/10.3390/ijgi14030109)
- **ABNT:** XIA, W. *et al*. Dynamic load balancing based on hypergraph partitioning for
  parallel geospatial cellular automata models. *ISPRS International Journal of
  Geo-Information*, Basel, v. 14, n. 3, p. 109, 2025. DOI: 10.3390/ijgi14030109.
- **Resumo:** em autômatos celulares geoespaciais paralelos (mudança de uso e cobertura do solo),
  a distribuição do custo de cálculo muda ao longo da simulação, desbalanceando os processos. O
  artigo redistribui os subdomínios dinamicamente por particionamento de hipergrafos conforme a
  carga observada e propõe o mecanismo MSCF (*Migrated-SubCellspaces-First*), que usa comunicação
  não bloqueante para reduzir o custo de migrar carga. Com dados da Califórnia, o balanceamento
  dinâmico melhorou o desempenho em **62,59% com 16 processos** em relação ao balanceamento
  estático.
- **No trabalho:** **melhoria candidata** de balanceamento dinâmico de carga. Na nossa simulação só
  os ignorantes contam vizinhos, então faixas com mais ignorantes custam mais.
- **Lido:** resumo oficial (Crossref).

---

## 📈 Métricas de desempenho

### 16. Amdahl (1967) — *Validity of the single processor approach to achieving large scale computing capabilities*

- **Autor:** Gene M. Amdahl (IBM, Sunnyvale)
- **Publicado em:** *AFIPS Spring Joint Computer Conference* (AFIPS '67), Atlantic City,
  18–20 abr. 1967, p. 483–485
- **Texto completo:** [PDF](https://www3.cs.stonybrook.edu/~rezaul/Spring-2019/CSE613/reading/Amdahl-1967.pdf)
  (cópia pública numa página de disciplina da Stony Brook University; o registro na ACM não aparece
  como aberto). A lei também está explicada na seção 2.2.3 de Eijkhout, Chow e van de Geijn
  (entrada 11), de licença aberta
- **DOI:** [10.1145/1465482.1465560](https://doi.org/10.1145/1465482.1465560)
- **ABNT:** AMDAHL, G. M. Validity of the single processor approach to achieving large scale
  computing capabilities. *In*: AFIPS SPRING JOINT COMPUTER CONFERENCE, 1967, Atlantic City.
  *Proceedings* […]. New York: ACM, 1967. p. 483–485. DOI: 10.1145/1465482.1465560.
- **Resumo:** texto que deu origem à **lei de Amdahl**: a parte do programa que não pode ser
  paralelizada limita o *speedup* máximo, por mais processadores que se usem.
- **No trabalho:** análise dos experimentos (parte serial: criar a grade, distribuir as faixas,
  redução e decisão de parada a cada geração).
- **Lido:** metadados (Crossref) e a explicação da lei no livro de Eijkhout; o artigo original não
  foi lido.

### 17. Gustafson (1988) — *Reevaluating Amdahl's law*

- **Autor:** John L. Gustafson
- **Publicado em:** *Communications of the ACM*, v. 31, n. 5, p. 532–533, maio 1988
- **Texto completo:** [ACM Digital Library (PDF)](https://dl.acm.org/doi/pdf/10.1145/42411.42415)
  (acervo 1951–2000 aberto, como na entrada 10)
- **DOI:** [10.1145/42411.42415](https://doi.org/10.1145/42411.42415)
- **ABNT:** GUSTAFSON, J. L. Reevaluating Amdahl's law. *Communications of the ACM*, New York,
  v. 31, n. 5, p. 532–533, 1988. DOI: 10.1145/42411.42415.
- **Resumo:** propõe o ***speedup* escalado** (lei de Gustafson): quando o tamanho do problema
  cresce junto com o número de processadores, a fração serial perde peso e o *speedup* pode crescer
  quase linearmente.
- **No trabalho:** experimentos de escalabilidade fraca (grade maior com mais processos).
- **Lido:** metadados (Crossref) e a explicação da lei no livro de Eijkhout (seção 2.2.3); o
  artigo original não foi lido.

---

## 🌐 Sistemas distribuídos

### 18. Van Steen e Tanenbaum (2023) — *Distributed systems*

- **Autores:** Maarten van Steen; Andrew S. Tanenbaum
- **Publicado em:** 4. ed., distributed-systems.net, 2023 (versão 4.03, jan. 2025, com pequenas
  correções)
- **Texto completo:** [distributed-systems.net/index.php/books/ds4](https://www.distributed-systems.net/index.php/books/ds4/).
  Os autores oferecem gratuitamente uma cópia digital **personalizada** (o livro não tem licença
  aberta: "todos os direitos reservados")
- **ABNT:** VAN STEEN, M.; TANENBAUM, A. S. *Distributed systems*. 4. ed. [*S. l.*]:
  distributed-systems.net, 2023. Disponível em:
  https://www.distributed-systems.net/index.php/books/ds4/. Acesso em: 22 nov. 2026.
- **Resumo:** livro-texto geral de sistemas distribuídos. O site também disponibiliza *slides* e o
  código dos exemplos.
- **No trabalho:** arquitetura coordenador–*workers*, comunicação por *sockets* e sincronização na
  versão distribuída.
- **Lido:** página do livro. **Conferir** no sumário da 4.ª edição os capítulos que serão citados.

---

## 🐍 Python

### 19. Gross (2023) — PEP 703: *Making the Global Interpreter Lock optional in CPython*

- **Autor:** Sam Gross (patrocinador: Łukasz Langa)
- **Publicado em:** *Python Enhancement Proposals*, criada em 9 jan. 2023; status *Final*
  (aceita em 24 out. 2023), alvo: Python 3.13
- **Texto completo:** [peps.python.org/pep-0703](https://peps.python.org/pep-0703/)
- **ABNT:** GROSS, S. *PEP 703*: making the global interpreter lock optional in CPython.
  [*S. l.*]: Python Software Foundation, 2023. Disponível em: https://peps.python.org/pep-0703/.
  Acesso em: 22 nov. 2026.
- **Resumo:** o GIL impede que várias *threads* executem código Python ao mesmo tempo, o que
  dificulta usar CPUs com vários núcleos. A PEP propõe uma opção de compilação do CPython
  (`--disable-gil`) para rodar sem o GIL. A motivação relata que as alternativas atuais, como o
  `multiprocessing`, têm custos de comunicação entre processos, serialização e memória.
- **No trabalho:** explica por que, no Python 3.12 usado pelo grupo, `threading` não acelera o
  cálculo e a versão paralela usa processos.
- **Lido:** texto da PEP (cabeçalho, *Abstract* e *Motivation*).

### 20. Python Software Foundation — glossário, *global interpreter lock* (Python 3.12)

- **Autor:** Python Software Foundation
- **Publicado em:** documentação oficial do Python 3.12 (licença PSF)
- **Texto completo:** [docs.python.org/3.12/glossary.html#term-global-interpreter-lock](https://docs.python.org/3.12/glossary.html#term-global-interpreter-lock)
- **ABNT:** PYTHON SOFTWARE FOUNDATION. Glossary: global interpreter lock. *In*: PYTHON
  SOFTWARE FOUNDATION. *Python 3.12 documentation*. [*S. l.*], [20--]. Disponível em:
  https://docs.python.org/3.12/glossary.html#term-global-interpreter-lock. Acesso em:
  22 nov. 2026.
- **Resumo:** define o GIL como o mecanismo usado pelo interpretador CPython para garantir que
  **só uma *thread* execute *bytecode* Python por vez**. Isso simplifica a implementação, tornando o
  modelo de objetos seguro contra acesso concorrente, "à custa de boa parte do paralelismo
  oferecido por máquinas multiprocessador". Alguns módulos de extensão liberam o GIL em tarefas
  pesadas (compressão, *hash*), e o GIL é sempre liberado durante E/S.
- **No trabalho:** definição oficial do GIL citada na seção da versão paralela, junto com a medição
  do modo *threads*.
- **Lido:** verbete completo.

### 21. Python Software Foundation — `multiprocessing.shared_memory` (Python 3.12)

- **Autor:** Python Software Foundation
- **Publicado em:** documentação oficial do Python 3.12 (módulo criado no Python 3.8; licença PSF)
- **Texto completo:** [docs.python.org/3.12/library/multiprocessing.shared_memory.html](https://docs.python.org/3.12/library/multiprocessing.shared_memory.html)
- **ABNT:** PYTHON SOFTWARE FOUNDATION. *multiprocessing.shared_memory*: shared memory for direct
  access across processes. *In*: PYTHON SOFTWARE FOUNDATION. *Python 3.12 documentation*.
  [*S. l.*], [20--]. Disponível em:
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

## 🚫 Retiradas por não serem de acesso aberto

Estas obras exigem assinatura ou login institucional e não têm cópia aberta confirmada. Foram
substituídas; algumas ainda estão citadas no relatório e precisam ser trocadas lá.

| Obra | Chave no `main.bib` | Citada no relatório | Substituída por |
|---|---|---|---|
| Daley e Kendall (1964), *Epidemics and rumours*, *Nature* | `DaleyKendall1964` | fundamentação | Moreno, Nekovee e Pacheco (2004); Nekovee et al. (2007) |
| Granovetter (1978), *Threshold models of collective behavior* | `Granovetter1978` | fundamentação | Watts (2002) |
| Vosoughi, Roy e Aral (2018), *The spread of true and false news online*, *Science* | `Vosoughi2018` | introdução | Del Vicario et al. (2016) |
| Wolfram (1983), *Statistical mechanics of cellular automata* | `Wolfram1983` | fundamentação | Berto e Tagliabue (SEP) |
| Bandini, Mauri e Serra (2001), *Cellular automata: from a theoretical parallel computational model…* | — | — | Berto e Tagliabue (SEP); Marzolla (2018) |
| Mattson, Sanders e Massingill (2004), *Patterns for parallel programming* (livro) | — | — | Massingill, Mattson e Sanders (2005), PLoP |
| Pacheco (2011), *An introduction to parallel programming* | `Pacheco2011` | fundamentação | Eijkhout, Chow e van de Geijn (2016) |
| Van Steen e Tanenbaum (2017), 3. ed. | `Tanenbaum2017` | fundamentação | mesma obra, 4. ed. (2023), cópia gratuita |

---

## ✍️ Como acrescentar uma referência

1. Só fontes com **texto completo aberto**: arXiv, PubMed Central, repositórios institucionais,
   acervo aberto da ACM (1951–2000), periódicos de acesso aberto, livros com licença aberta ou
   distribuídos gratuitamente pelos autores, documentação oficial. Para conferir, procure o DOI em
   `https://api.openalex.org/works/doi:<doi>` (campo `open_access`).
2. Confira autores e dados no registro do DOI (`https://doi.org/<doi>`) ou na página da obra.
3. Acrescente a entrada aqui, na seção do tema, com o link do texto completo e a linha **Lido**.
4. Acrescente a entrada BibTeX no `main.bib` do Overleaf e cite no texto com `\cite{chave}` ou
   `\citeonline{chave}`.
