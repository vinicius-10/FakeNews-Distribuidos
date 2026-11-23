# 📰 Propagação de Fake News em Sistemas Paralelos e Distribuídos

> Simulação da propagação de *fake news* em uma população representada por um autômato celular, nas versões sequencial, paralela e distribuída, desenvolvida durante a disciplina de Sistemas Distribuídos da UTFPR.

<div align="left">
  <img src="https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow" alt="Status">
  <img src="https://img.shields.io/badge/Linguagem-Python_3.12-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/Paralelismo-Threads_%2F_Processos-8A2BE2" alt="Paralelismo">
  <img src="https://img.shields.io/badge/Distribuído-Sockets-0A9396" alt="Sockets">
  <img src="https://img.shields.io/badge/Relatório-LaTeX_(abnTeX2)-008080?logo=latex&logoColor=white" alt="LaTeX">
</div>


## 📑 Sumário
- [Sobre o Projeto](#-sobre-o-projeto)
- [Objetivo](#-objetivo)
- [Modelo Computacional](#-modelo-computacional)
- [Andamento](#-andamento)
- [Conceitos Aplicados](#-conceitos-aplicados)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Como Executar](#-como-executar)
- [Como Contribuir](#-como-contribuir)
- [Relatório](#-relatório)
- [Equipe](#-equipe)

---

## 💜 Sobre o Projeto
O trabalho parte de uma simulação **sequencial** em Python, fornecida na disciplina, e a transforma em versões **paralela** e **distribuída**, comparando o desempenho entre elas.

A população é uma matriz bidimensional em que cada pessoa pode ignorar a notícia, espalhá-la ou já ter deixado de espalhá-la. A cada geração, a notícia se propaga entre vizinhos, como num autômato celular. Como cada célula da nova geração depende só da geração anterior, o cálculo pode ser dividido entre *threads*, processos e máquinas, desde que todos sincronizem a cada geração.

As três versões devem produzir **exatamente o mesmo resultado** para os mesmos parâmetros; a diferença está apenas em como o trabalho é dividido e sincronizado.

## 🎯 Objetivo
- Compreender e documentar o modelo e a implementação sequencial
- Desenvolver uma versão **paralela** com divisão explícita da matriz entre *threads*/processos, sem condições de corrida
- Desenvolver uma versão **distribuída** com *sockets*, sincronizando as fronteiras da matriz entre processos/máquinas
- Garantir a consistência das gerações e o mesmo resultado lógico nas três versões
- Medir e comparar **speedup**, **eficiência**, gargalos e custo de comunicação
- Propor e avaliar melhorias no modelo e na implementação

## 🧮 Modelo Computacional
| Estado | Significado |
|---|---|
| `0` Ignorante | ainda não recebeu ou não acredita na notícia |
| `1` Espalhador | acredita e compartilha a notícia |
| `2` Inativo | recebeu a notícia, mas não compartilha mais |

Regras de transição (vizinhança de Moore, até 8 vizinhos; bordas fixas):
- um **ignorante** vira **espalhador** se tiver pelo menos `limiar` vizinhos espalhadores;
- um **espalhador** vira **inativo** na geração seguinte;
- um **inativo** permanece inativo.

A grade inicial é sorteada com semente fixa e as regras são determinísticas, então os resultados são reproduzíveis e comparáveis célula a célula entre as versões. A simulação termina quando acabam as gerações ou os espalhadores.

## 🗺️ Andamento
| Etapa | Situação |
|---|---|
| Versão sequencial (fornecida) | ✅ Disponível |
| Versão sequencial refatorada (núcleo comum) | ✅ Implementada |
| Versão paralela (processos e threads) | ✅ Implementada |
| Versão distribuída (sockets TCP) | ✅ Implementada |
| Testes de equivalência entre as versões | ✅ Implementados |
| Melhorias (6) | ✅ Implementadas e medidas |
| Experimentos de desempenho (medição + tabelas + gráficos) | ✅ Medidos na máquina do grupo |
| Relatório e apresentação | 🔄 Em escrita |

## 📚 Conceitos Aplicados
| Conceito | Onde aparece |
|---|---|
| Autômato celular e vizinhança de Moore | Modelo da simulação (todas as versões) |
| Atualização síncrona (*double buffering*) | Cálculo de cada geração a partir da anterior |
| Decomposição de domínio | Divisão da matriz em faixas entre *threads*/processos |
| Sincronização por barreira | Fim de cada geração na versão paralela |
| Troca de bordas (*halo*) | Linhas de fronteira trocadas entre processos na versão distribuída |
| Redução global | Contagem de espalhadores para decidir o fim da simulação |
| *Speedup*, eficiência e leis de Amdahl e Gustafson | Análise dos experimentos |

## 🛠 Tecnologias Utilizadas
- Linguagem: Python 3.12 (biblioteca padrão)
- Paralelismo: `threading` / `multiprocessing` (divisão explícita do trabalho)
- Comunicação distribuída: *sockets* TCP
- Relatório: LaTeX com o modelo UTFPR (abnTeX2), editado no Overleaf
- Versionamento: Git + GitHub

> Por exigência da disciplina, o cálculo da próxima geração **não** usa paralelização implícita (NumPy vetorizado, Numba, Cython, GPU ou *frameworks* paralelos): toda a divisão do trabalho é implementada pelo grupo.

## 📂 Estrutura do Projeto
```
.
├── sequencial/
│   ├── fakenews_sequencial_original.py   # Versão fornecida na disciplina (referência, não alterar)
│   └── fakenews_sequencial.py            # Versão refatorada: núcleo comum, 1 processo
├── comum/                                # Código compartilhado pelas três versões
│   ├── modelo.py                         # Grade em bytes com moldura, cálculo de uma faixa, contagem
│   ├── parametros.py                     # Parâmetros e linha de comando; estado inicial (semente 42)
│   ├── saida.py                          # Impressão no formato do professor
│   ├── estatisticas.py                   # Melhoria: estatísticas e perfil de tempo (CSV)
│   └── visualizacao.py                   # Melhoria: animação da grade em HTML
├── paralelo/
│   └── fakenews_paralelo.py              # Processos + memória compartilhada (ou threads), barreiras
├── distribuido/
│   ├── protocolo.py                      # Mensagens com tamanho no cabeçalho (TCP)
│   ├── coordenador.py                    # Distribui as faixas, soma as contagens, decide a parada
│   ├── worker.py                         # Calcula uma faixa e troca as bordas com os vizinhos
│   └── executar_local.py                 # Coordenador + workers nesta máquina (testes e demonstração)
├── testes/                               # Testes de equivalência com a versão do professor
├── experimentos/                         # Medição de desempenho, análise e gráficos
│   ├── medir.py                          # Baterias de medição (aquecimento + repetições, CSV)
│   ├── analisar.py                       # Speedup, eficiência, Karp-Flatt, Amdahl, Gustafson
│   ├── perfis.py                         # Cálculo x comunicação x espera por worker
│   └── resultados/                       # CSVs, tabelas.md, perfis.md e gráficos
├── relatorio/                            # Cópia do relatório (LaTeX) mantida no Overleaf
├── .github/pull_request_template.md      # Modelo de descrição dos pull requests
├── CONTRIBUTING.md                       # Guia de contribuição do grupo
└── README.md
```

### Como as versões se dividem
- **Divisão da grade:** faixas horizontais de linhas contíguas, uma por *worker*, com tamanhos que diferem no máximo em 1 linha.
- **Grade em memória:** vetor de bytes (1 byte por célula) com uma linha de zeros em cima e embaixo (moldura). A moldura faz o papel da borda fixa e, na versão distribuída, do *halo*.
- **Paralela:** as duas grades (atual e próxima) ficam em memória compartilhada; cada geração tem duas barreiras: uma depois do cálculo e outra depois da decisão de parar.
- **Distribuída:** o coordenador gera a grade uma vez, envia as faixas, soma as contagens e decide a parada; os *workers* trocam as bordas **direto entre si** (cadeia), em ordem par/ímpar para não haver *deadlock*.

## ▶️ Como Executar
Requisito: **Python 3.12** (ou superior), sem dependências externas. Todos os comandos rodam a partir da raiz do repositório, iguais no Windows e no Linux (use `py` ou `python3` no lugar de `python` se for o caso).

Parâmetros comuns a todas as versões (padrões iguais aos do professor):

| Parâmetro | Padrão | Significado |
|---|---|---|
| `--linhas`, `--colunas` | 100, 100 | tamanho da grade |
| `--geracoes` | 50 | número máximo de gerações |
| `--percentual` | 0.05 | fração inicial de espalhadores |
| `--limiar` | 3 | vizinhos espalhadores para convencer (use 2 nos *benchmarks*) |
| `--semente` | 42 | semente da grade inicial |
| `--mostrar-grade` | — | imprime o canto da grade a cada geração |

```bash
# Sequencial do professor (parâmetros fixos no fim do arquivo)
python sequencial/fakenews_sequencial_original.py

# Sequencial refatorada
python -m sequencial.fakenews_sequencial --linhas 500 --colunas 500 --limiar 2

# Paralela: processos (padrão) ou threads
python -m paralelo.fakenews_paralelo --linhas 1000 --colunas 1000 --limiar 2 --trabalhadores 8
python -m paralelo.fakenews_paralelo --linhas 1000 --colunas 1000 --limiar 2 --trabalhadores 8 --modo threads

# Distribuída numa máquina só (coordenador + workers locais)
python -m distribuido.executar_local --workers 4 --linhas 1000 --colunas 1000 --limiar 2
```

**Distribuída entre computadores** (todos na mesma rede; no Windows, permita o Python no *firewall* em rede privada):
```bash
# Na máquina do coordenador (IP 192.168.0.10, por exemplo)
python -m distribuido.coordenador --host 0.0.0.0 --porta 5000 --workers 3 --linhas 2000 --colunas 2000 --limiar 2

# Em cada máquina, um worker por terminal (a ordem de chegada define a faixa)
python -m distribuido.worker --coordenador 192.168.0.10:5000 --escutar 0.0.0.0
```

### Melhorias
| Melhoria | Como usar |
|---|---|
| Grade compacta sem `deepcopy` | sempre ligada nas versões refatorada, paralela e distribuída |
| Estatísticas e perfil de tempo | `--estatisticas PASTA` grava CSVs por geração e por *worker* (cálculo, comunicação, espera) |
| Visualização gráfica | `--animacao grade.html` grava uma animação que abre no navegador |
| Resistência individual | `--resistencia MIN MAX`: limiar de cada pessoa sorteado entre MIN e MAX |
| Bots | `--bots 0.01`: 1% das células espalham sempre e nunca ficam inativas |
| Borda compactada em bits | `--bits` na distribuída: 1 bit por célula nas bordas, em vez de 1 byte |

As melhorias do modelo (resistência e bots) ficam desligadas por padrão, para reproduzir o professor; ligadas, as três versões continuam dando o mesmo resultado.

### Testes
```bash
python -m unittest discover -s testes -v
```
Comparam as versões refatorada, paralela (processos e threads) e distribuída com a versão do professor, geração a geração, em vários tamanhos, limiares e números de *workers*; com as melhorias ligadas, comparam com a sequencial refatorada.

### Experimentos
```bash
# bateria de fumaça: termina em segundos e confere se a medição funciona
python -m experimentos.medir --rapido

# baterias completas (ver experimentos/README.md para a lista e o porquê de separar)
python -m experimentos.medir --tamanhos 1000 2000 --workers 1 2 4 8 16 24 \
    --versoes paralela_processos --saida experimentos/resultados/medicoes_paralela.csv

# tabelas + resumo + gráficos a partir de todas as baterias gravadas
python -m experimentos.analisar

# perfil por worker: cálculo x comunicação x espera, e desbalanceamento
python -m experimentos.perfis
```

Os resultados ficam em [`experimentos/resultados/`](experimentos/resultados/): `medicoes_*.csv` (uma linha por repetição), `resumo.csv` (mediana, desvio, *speedup*, eficiência, Karp–Flatt, Amdahl e Gustafson), `tabelas.md`, `perfis.csv` e os gráficos. A mediana é a estatística reportada (aquecimento descartado + repetições) e cada execução grava o SHA-256 da grade final, então a bateria também serve de teste de equivalência em escala. `matplotlib` é opcional e só desenha os gráficos. Metodologia completa em [`experimentos/README.md`](experimentos/README.md).

## 🤝 Como Contribuir
Antes de contribuir, leia o [guia de contribuição](CONTRIBUTING.md): fluxo de *branches* e *pull requests*, padrão de commits, regras para o código rodar no Windows e no Linux, testes, experimentos e como referenciar o uso de IA.

## 📄 Relatório
O relatório técnico é escrito no Overleaf com o modelo LaTeX da UTFPR, e uma cópia é mantida em `relatorio/`. Para compilar localmente: pdfLaTeX + BibTeX + makeglossaries (por exemplo, `latexmk -pdf main.tex` dentro de `relatorio/`). Detalhes em [`relatorio/readme.md`](relatorio/readme.md).

O uso de ferramentas de IA generativa como apoio é registrado no apêndice do relatório, como exige a disciplina.

## 👥 Equipe
**Arthur Henrique Jardim**

[![GitHub](https://img.shields.io/badge/GitHub-arthur--hj-181717?logo=github&logoColor=white)](https://github.com/arthur-hj)

**João Alberto Benaci Torezan**

[![GitHub](https://img.shields.io/badge/GitHub-k7vinilstorage-181717?logo=github&logoColor=white)](https://github.com/k7vinilstorage)

**Rafael Munhoz Castro**

[![GitHub](https://img.shields.io/badge/GitHub-RafinhaW74-181717?logo=github&logoColor=white)](https://github.com/RafinhaW74)

**Vinicius Souza Dias**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-vinicius--dias--dev-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vinicius-dias-dev/)
[![GitHub](https://img.shields.io/badge/GitHub-vinicius--10-181717?logo=github&logoColor=white)](https://github.com/vinicius-10)
