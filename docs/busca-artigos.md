# 🔎 Busca de novos artigos

Registro da busca bibliográfica feita para **ampliar a fundamentação teórica** do trabalho, além
do que já está em [referencias.md](referencias.md). Aqui ficam os **candidatos**: artigos
encontrados, conferidos e avaliados, mas que ainda não entraram no relatório. Quando o grupo
decidir usar um deles, a entrada passa para o `referencias.md` e para o `main.bib` (ver
[Como promover um candidato](#-como-promover-um-candidato)).

> **Busca de 22/11/2026.** Feita com o buscador Exa (busca semântica na web) e conferida no
> registro do DOI na [Crossref](https://www.crossref.org/). Os resumos vêm do resumo oficial e,
> quando havia texto aberto, de trechos do texto completo (a linha **Lido** de cada entrada diz
> qual). Nenhum artigo foi lido inteiro: antes de citar uma afirmação específica, leia o trecho no
> original.
>
> **Conferência no IEEE Xplore (22/11/2026, à noite).** Com o acesso institucional da UTFPR
> ativo no IEEE Xplore ("*Access provided by: Universidade Tecnologica Federal do Parana*"), os
> artigos IEEE da lista foram abertos, o texto completo foi lido nos trechos indicados na linha
> **Lido** e o PDF foi baixado como teste. Os dados de cada um vêm do **BibTeX exportado pelo
> próprio IEEE Xplore** ([seção BibTeX](#-bibtex-dos-artigos-do-ieee-xplore)). A mesma busca
> achou dois candidatos novos (B20 e B21).

## 📑 Sumário

- [Bases de busca](#-bases-de-busca)
- [Protocolo da busca](#-protocolo-da-busca)
- [Resultado em uma tabela](#-resultado-em-uma-tabela)
- [Acesso verificado](#-acesso-verificado)
- [Candidatos por tema](#-candidatos-por-tema)
  - [Modelos de boato e autômatos celulares](#-modelos-de-boato-e-autômatos-celulares)
  - [Base para as melhorias do modelo](#-base-para-as-melhorias-do-modelo)
  - [Autômatos celulares em paralelo](#️-autômatos-celulares-em-paralelo)
  - [Medição e análise de desempenho](#-medição-e-análise-de-desempenho)
  - [Python e números aleatórios em paralelo](#-python-e-números-aleatórios-em-paralelo)
- [Encontrados e descartados](#️-encontrados-e-descartados)
- [BibTeX dos artigos do IEEE Xplore](#-bibtex-dos-artigos-do-ieee-xplore)
- [Próximas buscas](#-próximas-buscas)
- [Como promover um candidato](#-como-promover-um-candidato)

---

## 🏛️ Bases de busca

**Pela UTFPR (acesso pago liberado):** o [Portal de Periódicos da CAPES](https://www.periodicos.capes.gov.br/)
com login institucional (**Acesso CAFe** → UTFPR) libera o texto completo de:

| Base | O que cobre para este trabalho |
|---|---|
| [IEEE Xplore](https://ieeexplore.ieee.org/) | *IEEE TPDS*, *IEEE Computer*, conferências de computação paralela e de redes |
| [ACM Digital Library](https://dl.acm.org/) | *Communications of the ACM*, SC (*Supercomputing*), WWW |
| [ScienceDirect (Elsevier)](https://www.sciencedirect.com/) | *Physica A*, *Parallel Computing*, *Computers & Electrical Engineering* |
| [SpringerLink / Nature](https://link.springer.com/) | *Nature Physics*, *Journal of Statistical Physics* |
| [Scopus](https://www.scopus.com/) e [Web of Science](https://www.webofscience.com/) | busca por citações (quem cita quem) |

Fora da rede da UTFPR, entre pelo Portal CAPES → **Acesso CAFe** antes de abrir o link do DOI;
direto pelo DOI a editora pede pagamento.

**Abertas (sem login):** [arXiv](https://arxiv.org/) (cs.DC, physics.soc-ph),
[Google Acadêmico](https://scholar.google.com.br/), [Semantic Scholar](https://www.semanticscholar.org/),
[SBC OpenLib (SOL)](https://sol.sbc.org.br/) (ERAD, WSCAD, SBAC-PAD), [SciELO](https://www.scielo.br/),
[OSTI](https://www.osti.gov/), repositórios institucionais (ex.: CONICET) e periódicos de acesso
aberto (MDPI, *Nature Communications*).

## 🧭 Protocolo da busca

1. **Lacunas procuradas** (o que o `referencias.md` ainda não cobria): autômato celular aplicado a
   boato; modelos com céticos, checagem de fatos, *bots* e influenciadores (base das melhorias);
   resultados medidos de autômatos celulares em paralelo; métrica de Karp–Flatt; processadores
   com núcleos heterogêneos (a máquina do grupo tem núcleos P e E); metodologia de medição;
   reprodutibilidade de números aleatórios em paralelo.
2. **Consultas** (em inglês, que é a língua dos artigos):
   - `cellular automata rumor spreading model` · `cellular automata fake news propagation`
   - `rumor model skeptics` · `fact-checking hoax spreading model` · `social bots misinformation`
   - `influential spreaders complex networks` · `rumour spreading complex networks mean-field`
   - `parallel cellular automata MPI speedup` · `dynamic load balancing cellular automata`
   - `Karp Flatt serial fraction` · `Amdahl multicore era` · `hybrid P-core E-core parallel performance`
   - `scientific benchmarking parallel computing` · `counter-based parallel random numbers`
   - `Python multiprocessing threading GIL performance` · `mpi4py parallel distributed Python`
   - em português: `paralelização autômato celular jogo da vida speedup` (SBC/ERAD)
3. **Critérios de inclusão:** revisão por pares (periódico ou conferência) ou documento técnico
   de referência; relação direta com uma seção do relatório ou com uma melhoria; metadados
   conferíveis por DOI.
4. **Critérios de exclusão:** fora do escopo (ex.: autômato celular quântico); usa paralelismo
   implícito que o enunciado proíbe como solução; veículo sem revisão por pares quando existe
   alternativa revisada; duplicado do `referencias.md`.
5. **Conferência:** autores, ano, volume e páginas pelo `api.crossref.org/works/<doi>`.

## 📊 Resultado em uma tabela

**Prioridade:** 🔴 alta (usar) · 🟡 média (usar se a seção/melhoria correspondente existir) ·
⚪ baixa (só apoio). **Acesso:** 🔓 aberto · 🔐 pago, liberado pela CAPES/CAFe · ✅ texto completo
conferido no IEEE Xplore com o acesso da UTFPR.

| # | Referência | Tema | Base | Acesso | Prior. |
|---|---|---|---|---|---|
| B1 | [Nekovee et al. (2007)](#b1-nekovee-et-al-2007--theory-of-rumour-spreading-in-complex-social-networks) | Modelo de boato (Maki–Thompson) em redes | ScienceDirect / arXiv | 🔓 | 🔴 |
| B2 | [Wang, Wu e Chen (2014)](#b2-wang-wu-e-chen-2014--social-network-rumors-spread-model-based-on-cellular-automata) | Boato com autômato celular | **IEEE Xplore** | 🔐✅ | 🔴 |
| B3 | [Gardner (1970)](#b3-gardner-1970--the-fantastic-combinations-of-john-conways-new-solitaire-game-life) | Jogo da Vida (vizinhança de Moore) | JSTOR / Scientific American | 🔓 | 🟡 |
| B4 | [Shao, C. et al. (2024)](#b4-shao-c-et-al-2024--a-multi-information-dissemination-model-based-on-cellular-automata) | Várias informações num autômato celular | MDPI | 🔓 | 🟡 |
| B5 | [Li, Xiao e Wang (2016)](#b5-li-xiao-e-wang-2016--rumour-spreading-with-illusory-truth-effect) | Autômato celular + efeito de verdade ilusória | Inderscience | 🔐 | ⚪ |
| B6 | [Jin et al. (2013)](#b6-jin-et-al-2013--epidemiological-modeling-of-news-and-rumors-on-twitter) | Modelo SEIZ (céticos) | **ACM DL** | 🔓 | 🟡 |
| B7 | [Tambuscio et al. (2015)](#b7-tambuscio-et-al-2015--fact-checking-effect-on-viral-hoaxes) | Checagem de fatos contra boatos | **ACM DL** | 🔓 | 🟡 |
| B8 | [Amaral e Arenzon (2018)](#b8-amaral-e-arenzon-2018--rumor-propagation-meets-skepticism) | Ceticismo ativo e passivo | EPL / arXiv | 🔓 | 🟡 |
| B9 | [Shao, C. et al. (2018)](#b9-shao-c-et-al-2018--the-spread-of-low-credibility-content-by-social-bots) | *Bots* sociais | Nature Communications | 🔓 | 🟡 |
| B10 | [Kitsak et al. (2010)](#b10-kitsak-et-al-2010--identification-of-influential-spreaders-in-complex-networks) | Influenciadores | Nature Physics | 🔐 | 🟡 |
| B11 | [Millán et al. (2015)](#b11-millán-et-al-2015--performance-analysis-of-cellular-automata-hpc-implementations) | Autômato celular com MPI: *speedup* medido | ScienceDirect / CONICET | 🔓 | 🔴 |
| B12 | [Giordano et al. (2021)](#b12-giordano-et-al-2021--dynamic-load-balancing-in-parallel-execution-of-cellular-automata) | Balanceamento dinâmico em autômato celular | **IEEE Xplore** | 🔐✅ | 🔴 |
| B13 | [Stanislau, Osthoff e Silva (2015)](#b13-stanislau-osthoff-e-silva-2015--jogo-da-vida-em-intel-core-i7-xeon-e-xeon-phi) | Jogo da Vida em paralelo (ERAD-RJ) | LNCC (aberto) | 🔓 | ⚪ |
| B14 | [Karp e Flatt (1990)](#b14-karp-e-flatt-1990--measuring-parallel-processor-performance) | Métrica de Karp–Flatt | **ACM DL** | 🔓 | 🔴 |
| B15 | [Hill e Marty (2008)](#b15-hill-e-marty-2008--amdahls-law-in-the-multicore-era) | Amdahl em núcleos heterogêneos | **IEEE Xplore** | 🔓✅ | 🔴 |
| B16 | [Hoefler e Belli (2015)](#b16-hoefler-e-belli-2015--scientific-benchmarking-of-parallel-computing-systems) | Como medir e relatar desempenho | **ACM DL** | 🔓 | 🔴 |
| B17 | [Moori et al. (2024)](#b17-moori-et-al-2024--efficient-thread-tuning-for-asymmetric-multicores) | *Threads* em núcleos P/E (Alder Lake) | **IEEE Xplore** | 🔐✅ | ⚪ |
| B18 | [Dalcin et al. (2011)](#b18-dalcin-et-al-2011--parallel-distributed-computing-using-python) | Python distribuído; custo do *pickle* | ScienceDirect | 🔐 | 🟡 |
| B19 | [Salmon et al. (2011)](#b19-salmon-et-al-2011--parallel-random-numbers-as-easy-as-1-2-3) | Números aleatórios reprodutíveis em paralelo | **ACM DL** | 🔓 | 🟡 |
| B20 | [Giordano et al. (2019)](#b20-giordano-et-al-2019--strategies-for-parallel-execution-of-cellular-automata-in-distributed-memory-architectures) | Autômato celular em memória distribuída: partição, sobreposição, *multi-halo* | **IEEE Xplore** | 🔐✅ | 🔴 |
| B21 | [Liu et al. (2022)](#b21-liu-et-al-2022--sirqu-dynamic-quarantine-defense-model-for-online-rumor-propagation-control) | Quarentena de espalhadores (controle de boato) | **IEEE Xplore** | 🔐✅ | ⚪ |

**Recomendação para começar:** B14, B15 e B16 (análise dos experimentos), B11 (comparar nossos
números com um autômato celular paralelo publicado), B2 e B1 (fundamentação do modelo), B20 e
B12 (versão distribuída e suas melhorias: sobreposição, *halo* largo e balanceamento dinâmico).

## 🔓 Acesso verificado

**Verificação de 22/11/2026.** Para cada artigo: situação de acesso aberto no
[OpenAlex](https://openalex.org/) e **download de teste** do *link* (o PDF baixou e começa com
`%PDF`). À noite, os artigos do **IEEE Xplore** foram conferidos com o acesso institucional da
UTFPR (tabela [Liberado pela UTFPR no IEEE Xplore](#liberado-pela-utfpr-no-ieee-xplore)). As
outras editoras pagas (Nature, Elsevier, Inderscience) ainda não foram conferidas com o login.

### Texto completo disponível sem login

| # | Referência | Prior. | Onde ler | Como foi verificado |
|---|---|---|---|---|
| B14 | Karp e Flatt (1990) | 🔴 | [ACM DL (PDF)](https://dl.acm.org/doi/pdf/10.1145/78607.78614) | OpenAlex: grátis na editora (acervo antigo da ACM é aberto); o *download* automático foi barrado pelo anti-robô do site, mas o texto foi lido na busca |
| B15 | Hill e Marty (2008) | 🔴 | [PDF dos autores (UW-Madison)](https://research.cs.wisc.edu/multifacet/papers/ieeecomputer08_amdahl_multicore.pdf) | PDF baixado ✅ (no IEEE Xplore também abre com o acesso da UTFPR) |
| B16 | Hoefler e Belli (2015) | 🔴 | [PDF do autor (ETH Zürich)](https://htor.inf.ethz.ch/publications/img/hoefler-scientific-benchmarking.pdf) | PDF baixado ✅ (na ACM DL é pago) |
| B11 | Millán et al. (2015) | 🔴 | [Repositório CONICET](https://ri.conicet.gov.ar/handle/11336/38907) | OpenAlex: grátis na editora; texto completo lido na busca; o *download* automático caiu numa página intermediária do repositório |
| B1 | Nekovee et al. (2007) | 🔴 | [arXiv 0807.1458](https://arxiv.org/pdf/0807.1458) | PDF baixado ✅ |
| B3 | Gardner (1970) | 🟡 | [Cópia em Stanford](http://web.stanford.edu/class/sts145/Library/life.pdf) | PDF baixado ✅ |
| B4 | Shao, C. et al. (2024) | 🟡 | [MDPI](https://www.mdpi.com/2227-7390/12/6/914) | OpenAlex: acesso aberto (*gold*, licença CC BY); o *download* automático foi barrado pelo anti-robô do site |
| B6 | Jin et al. (2013) | 🟡 | [PDF dos autores (Virginia Tech)](https://people.cs.vt.edu/naren/papers/news-rumor-epi-snakdd13.pdf) | PDF baixado ✅ (na ACM DL é pago) |
| B7 | Tambuscio et al. (2015) | 🟡 | [Anais do WWW 2015](https://archives.iw3c2.org/www2015/documents/proceedings/companion/p977.pdf) | PDF baixado ✅ |
| B8 | Amaral e Arenzon (2018) | 🟡 | [arXiv 1810.03775](https://arxiv.org/pdf/1810.03775) | PDF baixado ✅ |
| B9 | Shao, C. et al. (2018) | 🟡 | [Nature Communications (PDF)](https://www.nature.com/articles/s41467-018-06930-7.pdf) | PDF baixado ✅ (acesso aberto) |
| B19 | Salmon et al. (2011) | 🟡 | [PDF dos autores](https://www.thesalmons.org/john/random123/papers/random123sc11.pdf) | PDF baixado ✅ (na ACM DL é pago) |
| B13 | Stanislau, Osthoff e Silva (2015) | ⚪ | [PDF (LNCC)](https://eradrj2015.lncc.br/forumic/146110.pdf) | PDF baixado ✅ |

A cópia do autor (pré-publicação ou versão do autor) pode ter diferenças pequenas de texto e de
paginação em relação à versão da editora. Para citar página, confira na versão da editora; a
referência no `main.bib` é sempre a da publicação oficial (DOI).

### Liberado pela UTFPR no IEEE Xplore

Conferido em 22/11/2026 com o acesso institucional ativo (a página mostra "*Access provided by:
Universidade Tecnologica Federal do Parana*"). Em todos, o texto completo aparece na própria
página do artigo e o PDF baixou (começa com `%PDF`). **Fora da rede da UTFPR** é preciso entrar
pelo Portal CAPES (Acesso CAFe) ou pelo login institucional do IEEE; pelo *link* direto o IEEE
pede pagamento.

| # | Referência | Prior. | Onde ler | Cópia aberta? |
|---|---|---|---|---|
| B2 | Wang, Wu e Chen (2014) | 🔴 | [IEEE Xplore 7051776](https://ieeexplore.ieee.org/document/7051776) | Não (fechado no OpenAlex) |
| B12 | Giordano et al. (2021) | 🔴 | [IEEE Xplore 9200755](https://ieeexplore.ieee.org/document/9200755) | Não |
| B20 | Giordano et al. (2019) | 🔴 | [IEEE Xplore 8671639](https://ieeexplore.ieee.org/document/8671639) | Não verificado |
| B15 | Hill e Marty (2008) | 🔴 | [IEEE Xplore 4563876](https://ieeexplore.ieee.org/document/4563876) | Sim, PDF dos autores (tabela de cima) |
| B17 | Moori et al. (2024) | ⚪ | [IEEE Xplore 10703981](https://ieeexplore.ieee.org/document/10703981) | Não |
| B21 | Liu et al. (2022) | ⚪ | [IEEE Xplore 9745750](https://ieeexplore.ieee.org/document/9745750) | Não verificado |

Duas obras do [referencias.md](referencias.md) também estão no IEEE Xplore e abriram com o mesmo
acesso: **Ding e He (2001)**, nos anais do SC '01 ([IEEE Xplore 1592831](https://ieeexplore.ieee.org/document/1592831),
DOI 10.1145/582034.582084, que faltava no `referencias.md`), e **Amdahl (1967)**, na reimpressão
do *IEEE Solid-State Circuits Society Newsletter* de 2007 ([IEEE Xplore 4785615](https://ieeexplore.ieee.org/document/4785615),
só PDF).

> **Atenção ao critério do grupo:** o `referencias.md` passou a aceitar **só fontes de acesso
> aberto** (commit `4f26dd7`). B2, B12, B17, B20 e B21 **não** têm cópia aberta: só entram no
> relatório se o grupo aceitar fontes lidas pelo acesso da UTFPR. B15 já tem cópia aberta.

### Só pelo Portal CAPES (falta conferir com o login CAFe)

| # | Referência | Prior. | Editora | Situação |
|---|---|---|---|---|
| B10 | Kitsak et al. (2010) | 🟡 | Nature Physics | A página da editora pede assinatura ("*Access through your institution*") |
| B18 | Dalcin et al. (2011) | 🟡 | ScienceDirect | OpenAlex diz "grátis na editora", mas o *download* deu 403; conferir |
| B5 | Li, Xiao e Wang (2016) | ⚪ | Inderscience | Fechado no OpenAlex; não se sabe se a Inderscience está no acervo da CAPES |

**Como conferir:** entrar em [periodicos.capes.gov.br](https://www.periodicos.capes.gov.br/) →
**Acesso CAFe** → UTFPR → login institucional; depois abrir o *link* do DOI de cada artigo **na
mesma janela**. Se aparecer o botão de PDF sem pedido de pagamento, mover a linha para a tabela
de cima.

---

## 📚 Candidatos por tema

### 🧠 Modelos de boato e autômatos celulares

#### B1. Nekovee et al. (2007) — *Theory of rumour spreading in complex social networks*

- **Autores:** Maziar Nekovee; Yamir Moreno; Ginestra Bianconi; Matteo Marsili
- **Publicado em:** *Physica A*, v. 374, n. 1, p. 457–470, jan. 2007
- **DOI:** [10.1016/j.physa.2006.07.017](https://doi.org/10.1016/j.physa.2006.07.017) ·
  arXiv: [0807.1458](https://arxiv.org/abs/0807.1458)
- **ABNT:** NEKOVEE, M. *et al*. Theory of rumour spreading in complex social networks.
  *Physica A*: statistical mechanics and its applications, [*s. l.*], v. 374, n. 1, p. 457–470,
  2007. DOI: 10.1016/j.physa.2006.07.017.
- **Resumo:** modelo estocástico geral de boato em redes sociais, com população dividida em
  ignorantes, espalhadores e abafadores (*stiflers*), seguindo Maki e Thompson: o ignorante vira
  espalhador com taxa λ ao contatar um espalhador; o espalhador vira abafador com taxa α ao contatar
  outro espalhador ou abafador; e acrescenta o **esquecimento** espontâneo (taxa δ). Deriva
  equações de campo médio e mostra que em grafos aleatórios existe um limiar crítico de taxa de
  espalhamento abaixo do qual o boato não se propaga, enquanto em redes livres de escala esse
  limiar tende a zero, por causa dos *hubs*.
- **No trabalho:** liga Daley–Kendall (já no `referencias.md`) aos modelos modernos; o estado
  "inativo" da simulação corresponde ao abafador, e o espalhador que dura uma geração é um caso
  extremo de esquecimento. O limiar crítico é um contraponto ao limiar de convencimento da grade.
- **Lido:** resumo oficial e seções 2, 3 e 6 (arXiv).

#### B2. Wang, Wu e Chen (2014) — *Social network rumors spread model based on cellular automata*

- **Autores:** Ailian Wang; Weili Wu; Junjie Chen
- **Publicado em:** *10th International Conference on Mobile Ad-hoc and Sensor Networks* (MSN
  2014), Maui (Havaí, EUA), 19–21 dez. 2014, IEEE, p. 236–242
- **DOI:** [10.1109/MSN.2014.39](https://doi.org/10.1109/MSN.2014.39) ·
  [IEEE Xplore](https://ieeexplore.ieee.org/document/7051776)
- **ABNT:** WANG, A.; WU, W.; CHEN, J. Social network rumors spread model based on cellular
  automata. *In*: INTERNATIONAL CONFERENCE ON MOBILE AD-HOC AND SENSOR NETWORKS, 10., 2014,
  Maui. *Proceedings* […]. [*S. l.*]: IEEE, 2014. p. 236–242. DOI: 10.1109/MSN.2014.39.
- **Resumo:** define o autômato celular como *A* = (*L*, *S*, *N*, *f*): grade com **contorno
  periódico**, vizinhança de **Moore de raio 1** e **sete estados** (não teve contato, teve
  contato, acredita, não acredita, repassa, questiona, desmente). As transições são
  **probabilísticas**, com quatro parâmetros (taxa de imunização *P1*, de crença *P2*, de
  transmissão *P3*, de dúvida *P4*); por exemplo, um vizinho que repassa leva a célula ao estado
  "teve contato", e um vizinho que desmente leva ao estado "questiona" com probabilidade *P1*. Em
  grade 50 × 50 com um espalhador inicial, mostra um **limiar de transmissão** (*P3* ≈ 0,07):
  acima dele o tempo para o boato cobrir a grade é quase constante; abaixo, cresce sem limite.
  Com 20 espalhadores iniciais, taxas de imunização maiores achatam e encurtam o pico de
  espalhadores. Compara a curva com uma rede real pequena (161 contatos do autor) e discute uma
  estratégia de imunização por informação positiva.
- **No trabalho:** é o precedente mais direto do nosso modelo (boato numa grade com vizinhança de
  Moore). As diferenças são bons pontos para a fundamentação: contorno periódico × **bordas
  fixas**; transição probabilística × **determinística**; sete estados × **três**. O limiar de
  transmissão conversa com o limiar de convencimento da nossa grade (com limiar 3 a simulação
  morre em ~3 gerações), e o estado "desmente" é base para uma melhoria de checadores/resistentes.
  Ressalva: a validação com dados reais é fraca (uma rede de 161 nós, sem método descrito) e o
  texto tem problemas de redação; citar como precedente do modelo, não como evidência empírica.
- **Lido:** texto completo (seções I a VI) no IEEE Xplore com acesso da UTFPR.

#### B3. Gardner (1970) — *The fantastic combinations of John Conway's new solitaire game "life"*

- **Autor:** Martin Gardner (coluna *Mathematical Games*)
- **Publicado em:** *Scientific American*, v. 223, n. 4, p. 120–123, out. 1970
- **Link:** [JSTOR 24927642](https://www.jstor.org/stable/24927642) ·
  [cópia aberta (Stanford)](http://web.stanford.edu/class/sts145/Library/life.pdf)
- **ABNT:** GARDNER, M. Mathematical games: the fantastic combinations of John Conway's new
  solitaire game "life". *Scientific American*, New York, v. 223, n. 4, p. 120–123, 1970.
- **Resumo:** apresenta o Jogo da Vida de Conway: grade de células, cada uma com **oito vizinhas
  (quatro ortogonais e quatro diagonais)**, regras locais de nascimento, sobrevivência e morte, e
  a exigência de que todas as mudanças de uma geração aconteçam **ao mesmo tempo** (o texto manda
  marcar nascimentos e mortes antes de aplicá-los, para que os novos não influenciem a geração
  corrente).
- **No trabalho:** exemplo clássico de autômato celular com a mesma vizinhança e a mesma
  atualização síncrona da simulação; justifica as duas grades (atual e próxima).
- **Lido:** texto completo (cópia aberta).

#### B4. Shao, C. et al. (2024) — *A multi-information dissemination model based on cellular automata*

- **Autores:** Changheng Shao; Fengjing Shao; Xin Liu; Dawei Yang; Rencheng Sun; Lili Zhang;
  Kaiwen Jiang
- **Publicado em:** *Mathematics* (MDPI), v. 12, n. 6, art. 914, mar. 2024 (acesso aberto)
- **DOI:** [10.3390/math12060914](https://doi.org/10.3390/math12060914)
- **ABNT:** SHAO, C. *et al*. A multi-information dissemination model based on cellular automata.
  *Mathematics*, [*s. l.*], v. 12, n. 6, p. 914, 2024. DOI: 10.3390/math12060914.
- **Resumo:** modelo SEInR em autômato celular para simular **várias informações** circulando ao
  mesmo tempo, com estados suscetível, exposto, *n* estados infectados (um por informação) e
  recuperado, e regras de transição que combinam a vizinhança local com a proporção global de
  usuários que expressam cada opinião. Com usuários do Weibo como células, a curva simulada teve
  similaridade acima de 98% com a participação real.
- **No trabalho:** base para a melhoria **múltiplas *fake news* concorrentes** (mais estados por
  célula, mesma estrutura de grade e de troca de bordas).
- **Lido:** resumo oficial e definições 1 a 4 (texto aberto).

#### B5. Li, Xiao e Wang (2016) — rumour spreading with illusory truth effect

- **Título completo:** *A social computing approach to rumour spreading with consideration of
  illusory truth effect and the latency reverse phenomenon*
- **Autores:** Jin Li; Renbin Xiao; Huimin Wang (a Crossref e o buscador divergem sobre qual é o
  sobrenome do primeiro autor; conferir no PDF)
- **Publicado em:** *International Journal of Innovative Computing and Applications*, v. 7, n. 2,
  p. 61, 2016 (Inderscience)
- **DOI:** [10.1504/IJICA.2016.077581](https://doi.org/10.1504/IJICA.2016.077581)
- **Resumo:** estende o modelo SIR num autômato celular com um fator de **efeito de verdade
  ilusória** (repetir uma afirmação aumenta a crença nela). Comparado com dados reais, o fator
  altera bastante a propagação e aparecem fenômenos de "latência reversa" e avalanche.
- **No trabalho:** apoio a uma melhoria em que o limiar de convencimento cai com a exposição
  repetida. Prioridade baixa (veículo de menor impacto).
- **Lido:** resumo oficial (via busca).

### 🧪 Base para as melhorias do modelo

#### B6. Jin et al. (2013) — *Epidemiological modeling of news and rumors on Twitter*

- **Autores:** Fang Jin; Edward Dougherty; Parang Saraf; Yang Cao; Naren Ramakrishnan
- **Publicado em:** *7th Workshop on Social Network Mining and Analysis* (SNAKDD '13), ACM,
  art. 8, p. 1–9, ago. 2013
- **DOI:** [10.1145/2501025.2501027](https://doi.org/10.1145/2501025.2501027) ·
  [PDF dos autores](https://people.cs.vt.edu/naren/papers/news-rumor-epi-snakdd13.pdf)
- **ABNT:** JIN, F. *et al*. Epidemiological modeling of news and rumors on Twitter. *In*:
  WORKSHOP ON SOCIAL NETWORK MINING AND ANALYSIS, 7., 2013, Chicago. *Proceedings* […].
  New York: ACM, 2013. p. 1–9. DOI: 10.1145/2501025.2501027.
- **Resumo:** ajusta modelos epidemiológicos a oito eventos do Twitter (quatro notícias e quatro
  boatos). O modelo **SEIZ** acrescenta o **exposto** (recebeu, mas demora a repassar) e o
  **cético** (recebeu e não repassa), e se ajusta aos dados bem melhor que o SIS, sobretudo no
  início da propagação.
- **No trabalho:** base para as melhorias **céticos** (célula que nunca vira espalhadora) e
  **atraso de exposição** (célula que precisa de mais de uma geração para ser convencida).
- **Lido:** resumo oficial e seção 4.2 (PDF dos autores).

#### B7. Tambuscio et al. (2015) — *Fact-checking effect on viral hoaxes*

- **Título completo:** *Fact-checking effect on viral hoaxes: a model of misinformation spread
  in social networks*
- **Autores:** Marcella Tambuscio; Giancarlo Ruffo; Alessandro Flammini; Filippo Menczer
- **Publicado em:** *24th International Conference on World Wide Web* (WWW '15 Companion), ACM,
  p. 977–982, maio 2015
- **DOI:** [10.1145/2740908.2742572](https://doi.org/10.1145/2740908.2742572) ·
  [PDF aberto](https://archives.iw3c2.org/www2015/documents/proceedings/companion/p977.pdf)
- **ABNT:** TAMBUSCIO, M. *et al*. Fact-checking effect on viral hoaxes: a model of
  misinformation spread in social networks. *In*: INTERNATIONAL CONFERENCE ON WORLD WIDE WEB, 24.,
  2015, Florence. *Proceedings* […]. New York: ACM, 2015. p. 977–982.
  DOI: 10.1145/2740908.2742572.
- **Resumo:** três estados — suscetível, crente (*believer*) e checador (*fact checker*) — com
  espalhamento das duas atitudes pelos vizinhos, verificação (crente → checador, probabilidade
  fixa) e esquecimento. Mostra que uma atividade de checagem relativamente pequena pode eliminar o
  boato mesmo com usuários crédulos, e deriva um limiar analítico para isso.
- **No trabalho:** base da melhoria **checadores de fatos / desmentido** concorrendo com a *fake
  news* na grade.
- **Lido:** resumo e seções do modelo e dos resultados analíticos (PDF aberto).

#### B8. Amaral e Arenzon (2018) — *Rumor propagation meets skepticism: a parallel with zombies*

- **Autores:** Marco Antonio Amaral; Jeferson J. Arenzon (UFRGS)
- **Publicado em:** *EPL (Europhysics Letters)*, v. 124, n. 1, art. 18007, 2018
- **DOI:** [10.1209/0295-5075/124/18007](https://doi.org/10.1209/0295-5075/124/18007) ·
  arXiv: [1810.03775](https://arxiv.org/abs/1810.03775)
- **ABNT:** AMARAL, M. A.; ARENZON, J. J. Rumor propagation meets skepticism: a parallel with
  zombies. *EPL*, [*s. l.*], v. 124, n. 1, p. 18007, 2018. DOI: 10.1209/0295-5075/124/18007.
- **Resumo:** modelo em que suscetíveis céticos se opõem ao boato de duas formas: **ativa**
  (o cético convence o espalhador a parar) e **passiva** (o exposto desiste por conta própria,
  como após checar a fonte). Com ceticismo forte, aparecem dois pontos fixos (biestabilidade) e o
  destino do boato depende da exposição inicial.
- **No trabalho:** reforça a melhoria de céticos e liga o resultado à **porcentagem inicial de
  espalhadores**, um dos parâmetros dos experimentos. Autores de universidade brasileira.
- **Lido:** resumo e seção 2 (arXiv).

#### B9. Shao, C. et al. (2018) — *The spread of low-credibility content by social bots*

- **Autores:** Chengcheng Shao; Giovanni Luca Ciampaglia; Onur Varol; Kai-Cheng Yang;
  Alessandro Flammini; Filippo Menczer
- **Publicado em:** *Nature Communications*, v. 9, art. 4787, nov. 2018 (acesso aberto)
- **DOI:** [10.1038/s41467-018-06930-7](https://doi.org/10.1038/s41467-018-06930-7)
- **ABNT:** SHAO, C. *et al*. The spread of low-credibility content by social bots. *Nature
  Communications*, [*s. l.*], v. 9, p. 4787, 2018. DOI: 10.1038/s41467-018-06930-7.
- **Resumo:** analisa 13,6 milhões de *tweets* com *links* para fontes de baixa credibilidade
  (maio/2016 a março/2017). Contas classificadas como *bots* eram 6% da amostra, mas responderam
  por 31% desses *tweets*; os *bots* agem nos primeiros segundos após a publicação e mencionam
  usuários influentes, e os humanos repassam o conteúdo de *bots* quase tanto quanto o de outros
  humanos.
- **No trabalho:** base da melhoria **bots** (células que espalham sempre e não ficam inativas).
  Complementa Vosoughi, Roy e Aral (2018), que já está no `referencias.md`.
- **Lido:** trechos do texto completo (resultados).

#### B10. Kitsak et al. (2010) — *Identification of influential spreaders in complex networks*

- **Autores:** Maksim Kitsak; Lazaros K. Gallos; Shlomo Havlin; Fredrik Liljeros; Lev Muchnik;
  H. Eugene Stanley; Hernán A. Makse
- **Publicado em:** *Nature Physics*, v. 6, n. 11, p. 888–893, 2010
- **DOI:** [10.1038/nphys1746](https://doi.org/10.1038/nphys1746)
- **ABNT:** KITSAK, M. *et al*. Identification of influential spreaders in complex networks.
  *Nature Physics*, [*s. l.*], v. 6, n. 11, p. 888–893, 2010. DOI: 10.1038/nphys1746.
- **Resumo:** mostra que os melhores espalhadores nem sempre são os mais conectados nem os mais
  centrais, e sim os do **núcleo** da rede pela decomposição *k-shell*; com vários espalhadores, a
  **distância entre eles** passa a ser o fator decisivo para o alcance.
- **No trabalho:** base da melhoria **influenciadores** (células com vizinhança maior ou peso
  maior) e de um experimento sobre a posição inicial dos espalhadores (agrupados × espalhados).
- **Lido:** resumo oficial.

#### B21. Liu et al. (2022) — *SIRQU: dynamic quarantine defense model for online rumor propagation control*

- **Autores:** Zhaoli Liu; Tao Qin; Qindong Sun; Shancang Li; Houbing Herbert Song; Zhouguo Chen
- **Publicado em:** *IEEE Transactions on Computational Social Systems*, v. 9, n. 6,
  p. 1703–1714, dez. 2022 (*online* em 31 mar. 2022)
- **DOI:** [10.1109/TCSS.2022.3161252](https://doi.org/10.1109/TCSS.2022.3161252) ·
  [IEEE Xplore](https://ieeexplore.ieee.org/document/9745750)
- **ABNT:** LIU, Z. *et al*. SIRQU: dynamic quarantine defense model for online rumor
  propagation control. *IEEE Transactions on Computational Social Systems*, [*s. l.*], v. 9,
  n. 6, p. 1703–1714, 2022. DOI: 10.1109/TCSS.2022.3161252.
- **Resumo:** propõe uma **quarentena dinâmica "suave"** para conter boatos em redes sociais
  *online*: além de suscetível, infectado e removido, o modelo SIRQU tem ignorantes e
  espalhadores **em quarentena**. Para baratear o controle, a quarentena só é aplicada aos nós
  mais influentes, escolhidos por otimização por enxame de partículas discreta; testado em bases
  públicas e no Sina Weibo.
- **No trabalho:** apoio a uma melhoria de **contenção** (células em quarentena que não repassam
  por algumas gerações) e à ligação entre influenciadores e controle do boato. Prioridade baixa:
  o modelo é em rede (grafo), não em grade, e a otimização foge do escopo.
- **Lido:** resumo oficial (o texto completo abriu no IEEE Xplore, mas não foi lido).

### ⚙️ Autômatos celulares em paralelo

#### B11. Millán et al. (2015) — *Performance analysis of Cellular Automata HPC implementations*

- **Autores:** Emmanuel N. Millán; Carlos S. Bederian; María Fabiana Piccoli; Carlos García
  Garino; Eduardo M. Bringa
- **Publicado em:** *Computers & Electrical Engineering*, v. 48, p. 12–24, nov. 2015
- **DOI:** [10.1016/j.compeleceng.2015.09.015](https://doi.org/10.1016/j.compeleceng.2015.09.015) ·
  [PDF aberto (CONICET)](https://ri.conicet.gov.ar/handle/11336/38907)
- **ABNT:** MILLÁN, E. N. *et al*. Performance analysis of cellular automata HPC implementations.
  *Computers & Electrical Engineering*, [*s. l.*], v. 48, p. 12–24, 2015.
  DOI: 10.1016/j.compeleceng.2015.09.015.
- **Resumo:** implementação do Jogo da Vida com MPI e decomposição de domínio, com troca de
  bordas e uma versão que **sobrepõe a comunicação ao cálculo do miolo**. Compara antes várias
  versões sequenciais (uma grade × duas grades, `char` × `int`). Mede escalabilidade forte e fraca
  e obtém eficiência de ~75–85% com 64 núcleos; com grade pequena (8192²) o *speedup* fica bem
  abaixo do ideal. Os contadores de *hardware* ligam as perdas a falhas de *cache*, desvios e
  acesso à memória: o problema é limitado por memória, não por cálculo.
- **No trabalho:** referência para **comparar nossos números** com um autômato celular paralelo
  publicado; justifica escalabilidade forte × fraca nos experimentos e explica por que grades
  pequenas não escalam. A sobreposição comunicação/cálculo é a mesma melhoria apontada por
  Bourached (2017).
- **Lido:** resumo e seções 2.3, 3.2 e 3.3 (PDF aberto).

#### B12. Giordano et al. (2021) — *Dynamic load balancing in parallel execution of cellular automata*

- **Autores:** Andrea Giordano; Alessio De Rango; Rocco Rongo; Donato D'Ambrosio; William Spataro
- **Publicado em:** *IEEE Transactions on Parallel and Distributed Systems*, v. 32, n. 2,
  p. 470–484, fev. 2021 (*online* em 18 set. 2020)
- **DOI:** [10.1109/TPDS.2020.3025102](https://doi.org/10.1109/TPDS.2020.3025102)
- **ABNT:** GIORDANO, A. *et al*. Dynamic load balancing in parallel execution of cellular
  automata. *IEEE Transactions on Parallel and Distributed Systems*, [*s. l.*], v. 32, n. 2,
  p. 470–484, 2021. DOI: 10.1109/TPDS.2020.3025102.
- **Resumo:** em aplicações espaciais com o domínio dividido em regiões, carga desigual faz os
  processos menos carregados esperarem os mais carregados na sincronização. O artigo deriva
  **expressões fechadas** para calcular a divisão ótima da carga durante a execução e um algoritmo
  de execução balanceada de autômatos celulares com MPI, que reduz o tempo em relação à versão sem
  balanceamento. O laço de cada nó (Algoritmo 1) é: enviar as bordas (*halo*) aos vizinhos,
  receber as deles, aplicar a regra de transição na própria região. No Algoritmo 2, de tempos em
  tempos cada nó manda ao **mestre** o seu **tempo por passo** e a sua carga (nº de colunas); o
  mestre calcula quantas colunas cada região deve ceder ou receber e os vizinhos trocam essas
  colunas. O balanceamento não roda a todo passo porque tem custo próprio. Com o modelo SciddicaT
  (deslizamento de terra), num nó de 16 núcleos, a versão balanceada chegou a **114% de melhora
  com 16 processos MPI**; também foi medida com um processo por nó do *cluster* (Gigabit
  Ethernet).
- **No trabalho:** base mais forte (IEEE TPDS, específica de autômato celular) para a melhoria
  **balanceamento dinâmico**: o coordenador recebe o tempo medido de cada *worker* e redimensiona
  as faixas de linhas, exatamente o esquema mestre–nós do Algoritmo 2. Também explica por que a
  divisão estática perde com núcleos P e E (o tempo por passo difere entre os *workers*).
  Complementa Xia et al. (2025), já no `referencias.md`.
- **Lido:** resumo e seções 2, 3 e 6 (texto completo no IEEE Xplore, acesso da UTFPR).

#### B13. Stanislau, Osthoff e Silva (2015) — Jogo da Vida em Intel Core i7, Xeon e Xeon Phi

- **Título completo:** *Avaliação de um problema fortemente acoplado nas arquiteturas Intel Core
  i7 e Intel Xeon com e sem Hyper Threading e Intel Xeon Phi*
- **Autores:** Rafael Lourenço Stanislau; Carla Osthoff; Mariano Pereira da Silva (LNCC)
- **Publicado em:** Escola Regional de Alto Desempenho do Rio de Janeiro (ERAD-RJ 2015), fórum de
  iniciação científica (resumo estendido, 2 p.)
- **Link:** [PDF](https://eradrj2015.lncc.br/forumic/146110.pdf)
- **Resumo:** Jogo da Vida 2000 × 2000, 5000 iterações, paralelizado com OpenMP. Melhor tempo com
  número de *threads* igual ao de núcleos físicos; o *Hyper-Threading* quase não ajuda porque cada
  *thread* acessa dados distintos; falhas de *cache* de último nível explicam a eficiência maior no
  i7 que no Xeon.
- **No trabalho:** apoio em português para discutir *threads* lógicas × núcleos físicos (a
  máquina do grupo tem 14 núcleos e 20 *threads*). Prioridade baixa: resumo estendido.
- **Lido:** texto completo.

#### B20. Giordano et al. (2019) — *Strategies for parallel execution of cellular automata in distributed memory architectures*

- **Autores:** Andrea Giordano; Alessio De Rango; Donato D'Ambrosio; Rocco Rongo; William Spataro
- **Publicado em:** *27th Euromicro International Conference on Parallel, Distributed and
  Network-Based Processing* (PDP 2019), Pavia (Itália), 13–15 fev. 2019, IEEE, p. 406–413
- **DOI:** [10.1109/EMPDP.2019.8671639](https://doi.org/10.1109/EMPDP.2019.8671639) ·
  [IEEE Xplore](https://ieeexplore.ieee.org/document/8671639)
- **ABNT:** GIORDANO, A. *et al*. Strategies for parallel execution of cellular automata in
  distributed memory architectures. *In*: EUROMICRO INTERNATIONAL CONFERENCE ON PARALLEL,
  DISTRIBUTED AND NETWORK-BASED PROCESSING, 27., 2019, Pavia. *Proceedings* […]. [*S. l.*]: IEEE,
  2019. p. 406–413. DOI: 10.1109/EMPDP.2019.8671639.
- **Resumo:** estudo preliminar, do mesmo grupo de B12, que compara três estratégias para
  executar autômatos celulares em memória distribuída com MPI: (1) **partição em uma dimensão
  (faixas) × em duas dimensões (blocos)**: com mais nós, a partição 2D vence porque troca menos
  bordas; (2) **intercalar comunicação e cálculo**: as células do miolo da região não dependem
  das bordas vizinhas e são calculadas enquanto as bordas chegam, reduzindo o tempo ocioso;
  (3) **multi-*halo***: bordas mais largas e cálculo redundante para trocar mensagens menos
  vezes. Medido com o modelo SciddicaT (grade 3593 × 3730, 1000 passos, sequencial de
  12.571,65 s), um processo MPI por nó de um *cluster* com Gigabit Ethernet; *speedup* contra a
  execução em um nó.
- **No trabalho:** é a referência mais direta para a **versão distribuída** e para três melhorias
  dela num só artigo de autômato celular: sobreposição comunicação/cálculo (hoje apoiada só por
  Bourached, 2017, que é dissertação no arXiv), *halo* largo (Ding e He, 2001) e partição 2D como
  alternativa às faixas. Também justifica medir com um processo por máquina ao falar de memória
  distribuída.
- **Lido:** resumo, seções II (estratégias) e III (avaliação) e conclusões (texto completo no
  IEEE Xplore, acesso da UTFPR).

### 📈 Medição e análise de desempenho

#### B14. Karp e Flatt (1990) — *Measuring parallel processor performance*

- **Autores:** Alan H. Karp; Horace P. Flatt (IBM)
- **Publicado em:** *Communications of the ACM*, v. 33, n. 5, p. 539–543, maio 1990
- **DOI:** [10.1145/78607.78614](https://doi.org/10.1145/78607.78614)
- **ABNT:** KARP, A. H.; FLATT, H. P. Measuring parallel processor performance. *Communications
  of the ACM*, New York, v. 33, n. 5, p. 539–543, 1990. DOI: 10.1145/78607.78614.
- **Resumo:** propõe a **fração serial determinada experimentalmente**,
  *f* = (1/*s* − 1/*p*) / (1 − 1/*p*), calculada a partir do *speedup* medido *s* com *p*
  processadores. *f* constante indica paralelismo limitado pelo programa; *f* crescendo de forma
  suave indica *overhead* de sincronização (granularidade fina demais); *f* variando de forma
  irregular indica **desbalanceamento de carga**. Diagnostica o que *speedup* e eficiência sozinhos
  não mostram.
- **No trabalho:** a skill `medir-desempenho` já calcula Karp–Flatt, mas o `referencias.md` não
  tem a fonte. Usar na seção de experimentos para explicar a queda de eficiência.
- **Lido:** trechos do texto (seções da nova métrica e do *speedup* escalado).

#### B15. Hill e Marty (2008) — *Amdahl's law in the multicore era*

- **Autores:** Mark D. Hill; Michael R. Marty
- **Publicado em:** *IEEE Computer*, v. 41, n. 7, p. 33–38, jul. 2008
- **DOI:** [10.1109/MC.2008.209](https://doi.org/10.1109/MC.2008.209) ·
  [PDF aberto (UW-Madison)](https://research.cs.wisc.edu/multifacet/papers/ieeecomputer08_amdahl_multicore.pdf)
- **ABNT:** HILL, M. D.; MARTY, M. R. Amdahl's law in the multicore era. *Computer*, [*s. l.*],
  v. 41, n. 7, p. 33–38, 2008. DOI: 10.1109/MC.2008.209.
- **Resumo:** estende a lei de Amdahl a *chips multicore* com um modelo de custo de núcleos e
  compara três projetos: **simétrico** (núcleos iguais), **assimétrico** (um núcleo forte e vários
  fracos) e dinâmico. O *chip* assimétrico pode dar *speedup* muito maior que o simétrico, mas o
  modelo não captura o custo de escalonar tarefas em núcleos diferentes.
- **No trabalho:** fundamenta a observação de que a máquina do grupo (6 núcleos P + 8 núcleos E)
  perde eficiência acima de ~6 *workers*: com divisão estática em faixas iguais, as faixas nos
  núcleos E terminam depois e todos esperam na barreira.
- **Lido:** trechos do PDF aberto (seções sobre Amdahl, *chips* simétricos e assimétricos e
  limitações) e a seção final no IEEE Xplore, que diz que escalonar tarefas em *chips*
  assimétricos pode ser difícil e acrescentar *overhead*, e lembra Gustafson (problemas maiores
  com mais núcleos).

#### B16. Hoefler e Belli (2015) — *Scientific benchmarking of parallel computing systems*

- **Título completo:** *Scientific benchmarking of parallel computing systems: twelve ways to
  tell the masses when reporting performance results*
- **Autores:** Torsten Hoefler; Roberto Belli (ETH Zürich)
- **Publicado em:** *SC15: International Conference for High Performance Computing, Networking,
  Storage and Analysis*, ACM, art. 73, p. 1–12, nov. 2015
- **DOI:** [10.1145/2807591.2807644](https://doi.org/10.1145/2807591.2807644) ·
  [PDF aberto](https://htor.inf.ethz.ch/publications/img/hoefler-scientific-benchmarking.pdf)
- **ABNT:** HOEFLER, T.; BELLI, R. Scientific benchmarking of parallel computing systems: twelve
  ways to tell the masses when reporting performance results. *In*: INTERNATIONAL CONFERENCE FOR
  HIGH PERFORMANCE COMPUTING, NETWORKING, STORAGE AND ANALYSIS, 2015, Austin. *Proceedings* […].
  New York: ACM, 2015. p. 1–12. DOI: 10.1145/2807591.2807644.
- **Resumo:** analisa 120 artigos de três grandes conferências e propõe **12 regras** para
  relatar desempenho de forma interpretável. Exemplos: dizer se o *speedup* é contra a melhor
  versão sequencial ou contra a paralela com 1 processo, e dar o tempo absoluto da base (regra 1);
  média aritmética só para custos (regra 3); relatar variabilidade ou intervalo de confiança
  (regra 5); documentar todo o ambiente e os fatores variados (regra 9).
- **No trabalho:** metodologia da seção de experimentos: *speedup* contra a versão **sequencial**,
  tempos absolutos, várias repetições com dispersão e registro de CPU, SO e versão do Python (o CSV
  do grupo já guarda o SO).
- **Lido:** trechos do PDF aberto (regras 1 a 5, 9, 10 e 12).

#### B17. Moori et al. (2024) — *Efficient thread tuning for asymmetric multicores*

- **Autores:** Marcelo K. Moori; Hiago Mayk G. de A. Rocha; Arthur F. Lorenzon; Antonio Carlos S.
  Beck
- **Publicado em:** *37th SBC/SBMicro/IEEE Symposium on Integrated Circuits and Systems Design*
  (SBCCI 2024), João Pessoa (PB), 2–6 set. 2024, IEEE, p. 1–5
- **DOI:** [10.1109/SBCCI62366.2024.10703981](https://doi.org/10.1109/SBCCI62366.2024.10703981)
- **ABNT:** MOORI, M. K. *et al*. Efficient thread tuning for asymmetric multicores. *In*:
  SYMPOSIUM ON INTEGRATED CIRCUITS AND SYSTEMS DESIGN, 37., 2024, João Pessoa. *Proceedings* […].
  [*S. l.*]: IEEE, 2024. p. 1–5. DOI: 10.1109/SBCCI62366.2024.10703981.
- **Resumo:** processadores assimétricos (núcleos de desempenho + núcleos eficientes) dificultam
  aproveitar o paralelismo. A biblioteca Mímir escolhe em tempo de execução o número ideal de
  *threads* por região paralela de programas OpenMP; num Intel Alder Lake, reduziu em média ~69–75%
  o produto energia × atraso. O artigo descreve o i9-12900K usado (8 núcleos P com
  *Hyper-Threading* + 8 núcleos E, 24 *threads*; os núcleos E em dois grupos de 4 que dividem uma
  cache L2 de 2 MB) e lembra que o OpenMP usa por padrão o **número máximo de *threads***, o que
  não é ótimo porque muitas aplicações escalam de forma sublinear. Compara também rodar só nos
  núcleos P ou só nos núcleos E.
- **No trabalho:** apoio à discussão de núcleos P/E (mesma arquitetura híbrida da máquina do
  grupo, i7-13650HX com 6P + 8E) e à ideia de que "mais *workers*" nem sempre é melhor. Grupo
  brasileiro (UFRGS). Prioridade baixa: foca em energia e OpenMP.
- **Lido:** resumo e seções II, IV e VI (texto completo no IEEE Xplore, acesso da UTFPR).

### 🐍 Python e números aleatórios em paralelo

#### B18. Dalcin et al. (2011) — *Parallel distributed computing using Python*

- **Autores:** Lisandro D. Dalcin; Rodrigo R. Paz; Pablo A. Kler; Alejandro Cosimo
- **Publicado em:** *Advances in Water Resources*, v. 34, n. 9, p. 1124–1139, set. 2011
- **DOI:** [10.1016/j.advwatres.2011.04.013](https://doi.org/10.1016/j.advwatres.2011.04.013)
- **ABNT:** DALCIN, L. D. *et al*. Parallel distributed computing using Python. *Advances in
  Water Resources*, [*s. l.*], v. 34, n. 9, p. 1124–1139, 2011.
  DOI: 10.1016/j.advwatres.2011.04.013.
- **Resumo:** apresenta o *MPI for Python* (mpi4py) e o *PETSc for Python*. Mede o custo da
  camada Python na comunicação: enviar objetos serializados com **pickle** custa ~80% a mais que C
  em mensagens pequenas e ~30% em grandes (Gigabit Ethernet), enquanto enviar **buffers de bytes**
  contíguos custa menos de 10%.
- **No trabalho:** justifica, na versão distribuída, enviar as linhas de *halo* como **bytes**
  (`bytes`/`bytearray`) pelo *socket* em vez de objetos serializados com `pickle`. O mpi4py em si
  **não** é usado (biblioteca externa; o trabalho usa só a biblioteca padrão).
- **Lido:** resumo e seções sobre comunicação e desempenho.

#### B19. Salmon et al. (2011) — *Parallel random numbers: as easy as 1, 2, 3*

- **Autores:** John K. Salmon; Mark A. Moraes; Ron O. Dror; David E. Shaw
- **Publicado em:** *SC11: International Conference for High Performance Computing, Networking,
  Storage and Analysis*, ACM, p. 1–12, nov. 2011 (finalista de melhor artigo)
- **DOI:** [10.1145/2063384.2063405](https://doi.org/10.1145/2063384.2063405) ·
  [PDF aberto](https://www.thesalmons.org/john/random123/papers/random123sc11.pdf)
- **ABNT:** SALMON, J. K. *et al*. Parallel random numbers: as easy as 1, 2, 3. *In*:
  INTERNATIONAL CONFERENCE FOR HIGH PERFORMANCE COMPUTING, NETWORKING, STORAGE AND ANALYSIS, 2011,
  Seattle. *Proceedings* […]. New York: ACM, 2011. p. 1–12. DOI: 10.1145/2063384.2063405.
- **Resumo:** geradores pseudoaleatórios comuns são transformações sequenciais de estado e
  escalam mal em paralelo. Os geradores **baseados em contador** calculam o *n*-ésimo número
  direto, *x*ₙ = *b*ₖ(*n*), sem depender do anterior. Derivando a chave e o contador de variáveis
  da aplicação (por exemplo, o índice da célula na grade) em vez de dados da máquina (número do
  processo), o resultado fica **igual com qualquer número de processos**, o que facilita depuração
  e repetibilidade.
- **No trabalho:** hoje só a grade inicial é aleatória (semente 42), gerada uma vez e distribuída.
  Se o grupo fizer uma melhoria **probabilística** (convencer com probabilidade), este é o
  argumento para sortear em função de (semente, geração, linha, coluna) e manter as três versões
  idênticas.
- **Lido:** resumo e seções 1 e 2 (PDF aberto).

---

## 🗑️ Encontrados e descartados

| Trabalho | Motivo |
|---|---|
| Tan, Zhang e Liu (2024), *Online-offline higher-order rumor propagation model based on quantum cellular automata* (*Applied Mathematics and Computation*, DOI 10.1016/j.amc.2023.128320) | Autômato celular quântico e complexos simpliciais: longe do modelo e do foco de computação paralela |
| Zhang, Li e Xiao (2013), *Hadoop cellular automata for identifying rumor in social networks* (ISCC-C, DOI 10.1109/ISCC-C.2013.76) | Usa Hadoop, um *framework* de paralelismo implícito que o enunciado proíbe; não serve nem como comparação de método |
| *Information propagation dynamic model based on rumors, antirumors, prom-rumors, and the dynamic game* (*IEEE Trans. Computational Social Systems*, v. 12, n. 1, 2025) | Teoria dos jogos + regressão + campo médio; não usa grade. Rever só se fizer "boato × desmentido" |
| Chen, Ma e Yang (2023), SEIOR (*Mathematics*, MDPI) · Yin et al. (2022), boato × contra-boato (*Chaos, Solitons & Fractals*) | Modelos de campo médio em redes; Tambuscio et al. (B7) cobre a mesma ideia de forma mais simples |
| Huo et al. (2018) e Cheng, Huo e Zhao (2020), modelos ISR com nós ativos (*Physica A*) | Variações de campo médio; Nekovee et al. (B1) já cobre a base |
| Gultom e Sarumaha (2025), JICDA; Zholdybay e Askar, CyberLeninka; "Python and parallel programming" (PDF sem veículo) | Comparam *threading* × *multiprocessing* em Python, mas em veículos sem revisão conhecida; a PEP 703 (no `referencias.md`) é fonte melhor |
| *Effects of hybrid CPU and cache architectures on parallel HPC/cloud applications* (arXiv 2608.23165) | Útil (Alder Lake, desbalanceamento, afinidade), mas é pré-publicação sem revisão; usar só se não houver alternativa — B15 e B17 cobrem o tema |
| Intel, *Managing performance with heterogeneous cores* (documentação do oneMKL) | Documentação de produto; pode ser citada como apoio técnico se precisar mostrar a recomendação "estático só nos núcleos P" |
| Ma, Chen e Meng (2012), *A performance analysis of the Game of Life based on parallel algorithm* (arXiv 1209.4408) | Sem revisão por pares e grades muito pequenas; Millán et al. (B11) é muito mais sólido |
| Xu (2026), ISCR; Zhao, Wang e Li (2026), SEITR | Veículos pouco conhecidos e modelos de campo médio |

## 🧾 BibTeX dos artigos do IEEE Xplore

Entradas montadas a partir do BibTeX que o próprio IEEE Xplore exporta (botão *Cite This* →
*BibTeX*), conferidas na página de cada artigo em 22/11/2026. Ajustes feitos para o `main.bib`
do relatório: chave no padrão `SobrenomeAno` já usado lá, título em caixa de sentença (como nas
entradas existentes), páginas com `--`, campo `keywords` removido e, nos anais, acrescentados
`address` (local do evento) e `publisher`, que o estilo `abntex2-alf` usa. **Ainda não foram
copiadas para o `main.bib`**: entram lá quando o grupo promover o candidato (ver
[Como promover um candidato](#-como-promover-um-candidato)).

```bibtex
%% ---------- Candidatos (este arquivo) ----------

@inproceedings{WangWuChen2014,
  author    = {Ailian Wang and Weili Wu and Junjie Chen},
  title     = {Social network rumors spread model based on cellular automata},
  booktitle = {Proceedings of the 10th International Conference on Mobile Ad-hoc and Sensor Networks (MSN)},
  year      = {2014},
  pages     = {236--242},
  address   = {Maui},
  publisher = {IEEE},
  doi       = {10.1109/MSN.2014.39},
}

@article{Giordano2021,
  author  = {Andrea Giordano and De Rango, Alessio and Rocco Rongo and Donato D'Ambrosio and William Spataro},
  title   = {Dynamic load balancing in parallel execution of cellular automata},
  journal = {IEEE Transactions on Parallel and Distributed Systems},
  year    = {2021},
  volume  = {32},
  number  = {2},
  pages   = {470--484},
  doi     = {10.1109/TPDS.2020.3025102},
}

@inproceedings{Giordano2019,
  author    = {Andrea Giordano and De Rango, Alessio and Donato D'Ambrosio and Rocco Rongo and William Spataro},
  title     = {Strategies for parallel execution of cellular automata in distributed memory architectures},
  booktitle = {Proceedings of the 27th Euromicro International Conference on Parallel, Distributed and Network-Based Processing (PDP)},
  year      = {2019},
  pages     = {406--413},
  address   = {Pavia},
  publisher = {IEEE},
  doi       = {10.1109/EMPDP.2019.8671639},
}

@article{HillMarty2008,
  author  = {Mark D. Hill and Michael R. Marty},
  title   = {{Amdahl's} law in the multicore era},
  journal = {Computer},
  year    = {2008},
  volume  = {41},
  number  = {7},
  pages   = {33--38},
  doi     = {10.1109/MC.2008.209},
}

@inproceedings{Moori2024,
  author    = {Marcelo K. Moori and Rocha, Hiago Mayk G. de A. and Arthur F. Lorenzon and Antonio Carlos S. Beck},
  title     = {Efficient thread tuning for asymmetric multicores},
  booktitle = {Proceedings of the 37th SBC/SBMicro/IEEE Symposium on Integrated Circuits and Systems Design (SBCCI)},
  year      = {2024},
  pages     = {1--5},
  address   = {Jo{\~a}o Pessoa},
  publisher = {IEEE},
  doi       = {10.1109/SBCCI62366.2024.10703981},
}

@article{Liu2022,
  author  = {Zhaoli Liu and Tao Qin and Qindong Sun and Shancang Li and Houbing Herbert Song and Zhouguo Chen},
  title   = {{SIRQU}: dynamic quarantine defense model for online rumor propagation control},
  journal = {IEEE Transactions on Computational Social Systems},
  year    = {2022},
  volume  = {9},
  number  = {6},
  pages   = {1703--1714},
  doi     = {10.1109/TCSS.2022.3161252},
}

%% ---------- Obras do referencias.md que também estão no IEEE Xplore ----------

@inproceedings{DingHe2001,
  author    = {Chris H. Q. Ding and Yun He},
  title     = {A ghost cell expansion method for reducing communications in solving {PDE} problems},
  booktitle = {Proceedings of the 2001 ACM/IEEE Conference on Supercomputing (SC '01)},
  year      = {2001},
  pages     = {55},
  address   = {Denver},
  publisher = {ACM/IEEE},
  doi       = {10.1145/582034.582084},
}

% Reimpressão de 2007 do artigo de 1967 (só PDF no IEEE Xplore). O main.bib já tem
% Amdahl1967 (anais originais da AFIPS); use esta entrada só se for citar a reimpressão.
@article{Amdahl2007reimpressao,
  author  = {Gene M. Amdahl},
  title   = {Validity of the single processor approach to achieving large scale computing capabilities},
  journal = {IEEE Solid-State Circuits Society Newsletter},
  year    = {2007},
  volume  = {12},
  number  = {3},
  pages   = {19--20},
  note    = {Reimpressão de: AFIPS Spring Joint Computer Conference, 1967, p. 483--485},
  doi     = {10.1109/N-SSC.2007.4785615},
}
```

Observações sobre os dados:

- **Ding e He (2001):** o IEEE registra o primeiro autor só como "C. Ding"; o nome completo
  (Chris H. Q. Ding) vem do relatório técnico LBNL e do OSTI. O IEEE também registra a página
  como 55 (o SC '01 numerou os artigos, não as páginas).
- **Moori et al. (2024):** o IEEE grafa o segundo autor como "Hiago Mayk G. De A. Rocha"; o
  sobrenome usado na citação é **Rocha** (por isso a forma `Rocha, Hiago Mayk G. de A.` no
  BibTeX). Conferir no PDF se o grupo for citar.
- **Hill e Marty (2008):** a revista se chama *Computer* (IEEE Computer Society); "IEEE Computer"
  é só o nome popular.

## 🔭 Próximas buscas

Buscas que valem a pena fazer **direto nas bases da CAPES** (com login CAFe), que têm filtros
melhores que a busca na web:

- ~~**IEEE Xplore**~~ — **feita em 22/11/2026** com o acesso da UTFPR. Consultas: `rumor
  spreading cellular automata model`, `parallel cellular automata MPI performance`, `parallel
  Game of Life speedup`, `halo exchange overlap communication computation stencil`, `Amdahl law
  heterogeneous multicore asymmetric`, `influential spreaders rumor model`, `Python
  multiprocessing parallel performance GIL`, entre outras. Resultado: B20 e B21 (novos); fora
  isso, só repetiu B2 e B12 ou trouxe trabalhos fora do escopo (detecção de *fake news* com
  aprendizado de máquina, Hadoop, autômato celular em GPU/*tensor cores*, que o enunciado não
  permite como solução).
- **ACM DL:** `"stencil" AND "load imbalance" AND "heterogeneous cores"`; também os artigos que
  **citam** Karp e Flatt (1990) e falam de *stencil*.
- **Scopus / Web of Science:** quem cita Wang, Wu e Chen (2014) — achar autômatos celulares de
  boato mais recentes e com mais citações.
- **SBC OpenLib (SOL):** anais do ERAD e do WSCAD com `autômato celular`, `stencil`, `Python`,
  `sockets` — fontes em português valorizam a fundamentação.
- **Livro-texto com DOI:** Gropp, Lusk e Skjellum, *Using MPI* (MIT Press), para a ordem de envio
  e recebimento que evita *deadlock* na troca de bordas, caso a banca peça fonte além de Mattson,
  Sanders e Massingill (2004).

## ✅ Como promover um candidato

1. Ler o artigo (pelo menos o trecho que vai ser citado) com acesso CAFe ou pelo *link* aberto.
2. Mover a entrada para o [referencias.md](referencias.md), na seção do tema, atualizando a linha
   **Lido**, e marcar aqui na tabela (ex.: "→ ref. 20").
3. Acrescentar a entrada BibTeX no `main.bib` do Overleaf e citar com `\cite{chave}` ou
   `\citeonline{chave}`.
