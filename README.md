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
| Versão paralela | ⏳ Em desenvolvimento |
| Versão distribuída | ⏳ Em desenvolvimento |
| Testes de equivalência entre as versões | ⏳ Planejado |
| Experimentos de desempenho | ⏳ Planejado |
| Melhorias e extensões do modelo | ⏳ Planejado |
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
│   └── fakenews_sequencial_original.py   # Versão fornecida na disciplina (referência)
├── relatorio/                            # Cópia do relatório (LaTeX) mantida no Overleaf
│   ├── main.tex                          # Arquivo principal
│   ├── capitulos/                        # Seções do relatório
│   ├── PreTexto/ e PosTexto/             # Resumo, siglas e apêndices
│   └── readme.md                         # Como compilar e mudanças no modelo UTFPR
├── .github/
│   └── pull_request_template.md          # Modelo de descrição dos pull requests
├── CONTRIBUTING.md                       # Guia de contribuição do grupo
└── README.md
```

As pastas das versões paralela e distribuída, dos testes e dos experimentos serão adicionadas conforme o desenvolvimento avançar.

## ▶️ Como Executar
1. Clone o repositório:
   ```bash
   git clone https://github.com/vinicius-10/FakeNews-Distribuidos.git
   cd FakeNews-Distribuidos
   ```
2. Tenha o **Python 3.12** (ou superior) instalado; não há dependências externas.
3. Execute a versão sequencial:
   ```bash
   python sequencial/fakenews_sequencial_original.py
   ```
   Os parâmetros (tamanho da grade, gerações, percentual inicial de espalhadores e limiar) ficam no fim do arquivo, na chamada de `executar_simulacao`.

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
