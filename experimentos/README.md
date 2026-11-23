# 📊 Experimentos de desempenho

Scripts de medição das três versões (sequencial, paralela e distribuída), da
análise dos resultados e dos gráficos do relatório.

Nada aqui faz parte da simulação: as versões continuam usando só a biblioteca
padrão do Python. `matplotlib` é usado **apenas** para desenhar os gráficos,
como o enunciado permite.

## Como rodar

Da raiz do repositório:

```bash
# bateria de fumaça: termina em segundos e serve para conferir se tudo funciona
python -m experimentos.medir --rapido

# 1) escalabilidade forte: grades 1000² e 2000², 1 a 24 trabalhadores
#    (escalabilidade = distribuída; a paralela é medida à parte, veja abaixo)
python -m experimentos.medir --tamanhos 1000 2000 --workers 1 2 4 8 16 24 \
    --versoes distribuida_local distribuida_bits \
    --saida experimentos/resultados/medicoes_escalabilidade.csv

# 2) versão paralela (a que foi otimizada com a cópia local da faixa)
python -m experimentos.medir --tamanhos 1000 2000 --workers 1 2 4 8 16 24 \
    --versoes paralela_processos --saida experimentos/resultados/medicoes_paralela.csv

# 3) efeito do GIL: só threads, uma grade
python -m experimentos.medir --tamanhos 1000 --workers 1 2 4 8 16 24 \
    --versoes paralela_threads --saida experimentos/resultados/medicoes_gil.csv

# 4) melhoria "grade compacta": professor x refatorada
python -m experimentos.medir --tamanhos 500 1000 2000 \
    --versoes sequencial_original sequencial --repeticoes 3 \
    --saida experimentos/resultados/medicoes_professor.csv

# 5) linha de base quente (a 1ª leitura do sequencial pode pegar a máquina fria)
python -m experimentos.medir --tamanhos 1000 2000 --versoes sequencial --repeticoes 7 \
    --saida experimentos/resultados/medicoes_baseline.csv

# 6) BATERIA DE PARÂMETROS: varia percentual de espalhadores e limiar (o que o
#    medir.py não faz, porque lá esses dois são valor único para a bateria toda).
#    Cada célula roda aquecimento + repetições e é conferida contra a sequencial.
python -m experimentos.bateria \
    --percentuais 0.01 0.05 0.10 0.20 --limiares 1 2 3 \
    --tamanhos 300 600 --geracoes 20 --workers 1 2 4 --repeticoes 3

# só o plano, sem executar (confere o tamanho da bateria antes de começar)
python -m experimentos.bateria --simular

# exporta os mesmos cenários para o setup de 3 máquinas
python -m experimentos.bateria --percentuais 0.05 --limiares 2 --tamanhos 2000 \
    --repeticoes 3 --exportar-cenarios experimentos/resultados/bateria/cenarios-3-maquinas.json

# analisar (aceita vários CSVs; as baterias são somadas)
python -m experimentos.analisar --csv experimentos/resultados/medicoes_escalabilidade.csv \
    experimentos/resultados/medicoes_paralela.csv experimentos/resultados/medicoes_gil.csv \
    experimentos/resultados/medicoes_professor.csv experimentos/resultados/medicoes_baseline.csv

# perfil por worker: cálculo x comunicação x espera, e desbalanceamento
python -m experimentos.perfis

# efeito das melhorias do MODELO (resistência individual e bots), não do desempenho
python -m experimentos.modelo
```

As baterias são divididas porque o código do professor é muito mais lento que as
versões refatoradas: medir tudo de uma vez levaria dezenas de minutos sem
necessidade. `analisar.py` aceita `--csv` repetido/ múltiplo e soma as medições,
então dividir não perde nada.

A paralela tem arquivo próprio porque foi **otimizada depois** da primeira
bateria (cópia local da faixa em vez de acessar a memória compartilhada célula a
célula). Misturar as medições antigas e novas na mesma mediana daria um número
que não corresponde a nenhuma das duas implementações.

Opcionalmente, instale o `matplotlib` para os gráficos:

```bash
pip install matplotlib
```

Sem ele, as tabelas e o `resumo.csv` são gerados do mesmo jeito.

## Metodologia (regras do `CONTRIBUTING.md`)

1. **Um único sistema operacional por gráfico.** Todas as medições ficam na
   mesma máquina; misturar Windows e Linux no mesmo gráfico invalida a
   comparação.
2. **1 execução de aquecimento descartada** e **pelo menos 5 repetições** por
   configuração, e a **mediana** é o número reportado.
3. **A máquina é registrada** em `resultados/ambiente.csv` (processador, núcleos
   físicos e lógicos, memória, sistema operacional, versão do Python).
4. **A base do *speedup* é dita explicitamente:** a versão sequencial
   refatorada, que usa o mesmo núcleo de cálculo das versões paralela e
   distribuída. O relatório também traz o *speedup* contra o código do
   professor, que é a outra linha de base.
5. **Limiar 2 nos *benchmarks*.** Com limiar 3 a simulação morre em cerca de 3
   gerações e não há trabalho suficiente para medir (ver `CONTRIBUTING.md`).

### O que entra no tempo

O tempo medido é o do **laço de gerações** (`tempo_laco_s`), igual nas três
versões: a grade inicial é gerada antes de começar a contar e, na paralela e na
distribuída, a criação de processos e as conexões também ficam de fora.

O `tempo_total_s` (que inclui criação de processos e conexões) vai na mesma
linha do CSV para a análise de custo de inicialização — é ele que mostra por
que vale a pena reaproveitar os *workers* entre gerações.

> **Atenção (desde 23 nov. 2026):** na distribuída, o `tempo_total_s` passou a
> começar **depois que todos os *workers* conectam** (distribuição das faixas,
> conexão dos vizinhos, laço e coleta). Os CSVs medidos antes disso incluem a
> subida dos processos *worker* na distribuída; não compare `tempo_total_s`
> antigo com novo nessa versão. O `tempo_laco_s` (base do *speedup*) não mudou.

### Correção verificada a cada execução

Cada execução grava o **SHA-256 da grade final**. Como todas as versões têm de
produzir a mesma grade, o `analisar.py` compara os hashes com o da sequencial e
denuncia qualquer divergência. Ou seja: a bateria de experimentos também é um
teste de equivalência em escala, além dos testes de `testes/`.

## Versões medidas

| Versão | O que é |
|---|---|
| `sequencial_original` | laço com as funções do professor (`deepcopy` por geração) — linha de base do trabalho |
| `sequencial` | versão refatorada sobre `comum/modelo.py` |
| `paralela_processos` | `multiprocessing` com memória compartilhada |
| `paralela_threads` | mesmo laço com *threads* — mostra o efeito do **GIL** |
| `distribuida_local` | coordenador + *workers* por *socket* TCP em `127.0.0.1` |
| `distribuida_bits` | a distribuída com a melhoria "borda compactada em bits" |

## Bateria de parâmetros (`bateria.py`)

O `medir.py` varia **tamanho, trabalhadores e versão**. `--percentual` e `--limiar`
entram como valor único, fixo para a bateria toda — o que impede responder "a taxa
inicial de espalhadores e o limiar mudam o custo de cada versão?".

O `bateria.py` monta o produto cartesiano:

```
percentuais × limiares × tamanhos × versões × trabalhadores
```

e, para cada célula, roda aquecimento + repetições. Saídas na pasta `--saida`:

| Arquivo | O que tem |
|---|---|
| `medicoes.csv` | uma linha por repetição, **no mesmo formato do `medir.py`** (mesmos campos, então `analisar.py` continua servindo) |
| `resumo.md` | uma seção por cenário: mediana, desvio, speedup, eficiência, gerações e veredito de equivalência |
| `ambiente.csv` | configuração da máquina, igual ao `medir.py` |
| `cenarios.json` | os mesmos cenários para o setup de 3 máquinas (`--exportar-cenarios`) |

**Cuidado que o script resolve:** `analisar.agrupar` agrupa por
`(versão, tamanho, workers)` e `analisar.verificar_equivalencia` compara hashes por
tamanho — as duas **ignoram `percentual` e `limiar`**, porque no `medir.py` eles são
constantes. Rodando a análise no CSV inteiro de uma bateria que varia os dois, a
mediana misturaria cenários diferentes e a equivalência acusaria divergência falsa
(percentuais diferentes geram grades diferentes por definição). Por isso o
`bateria.py` fatia o CSV por cenário antes de chamar essas funções; o
`testes/test_bateria.py` trava esse comportamento.

**Sobre a referência do speedup:** é a `sequencial` **do mesmo cenário**. Comparar
versões entre cenários diferentes não faz sentido — o trabalho muda com percentual
e limiar.

**Sobre poucas repetições:** com 1 repetição, um único outlier de agendamento do
sistema pode fazer a paralela de 1 worker parecer 2× mais rápida que a sequencial
(já aconteceu no `--rapida`). O relatório avisa quando `--repeticoes < 3`.

## Arquivos gerados

```
experimentos/resultados/
├── ambiente.csv               # configuração da máquina de medição
├── medicoes_escalabilidade.csv # distribuída (bytes e bits), 1000² e 2000²
├── medicoes_paralela.csv       # versão paralela já otimizada
├── medicoes_gil.csv            # threads × processos
├── medicoes_professor.csv      # professor × refatorada (grade compacta)
├── medicoes_baseline.csv       # linha de base quente, para o T1
├── resumo.csv                 # mediana, desvio, speedup, eficiência, Karp-Flatt,
│                              #   Amdahl e Gustafson de cada configuração
├── tabelas.md                 # tabelas prontas para colar no relatório
├── perfis.csv / perfis.md     # cálculo x comunicação x espera e desbalanceamento
├── modelo_geracoes.csv        # melhorias do modelo: contagem por geração e cenário
├── modelo_resumo.csv / modelo.md  # pico, alcance e duração de cada cenário
└── graficos/
    ├── speedup.png            # speedup × trabalhadores, um painel por tamanho
    ├── eficiencia.png         # eficiência × trabalhadores
    ├── gil.png                # threads × processos (escala log)
    ├── melhorias.png          # tempo com 1 trabalhador: impacto das melhorias
    └── modelo.png             # espalhadores e inativos por geração, por cenário
```

## Métricas calculadas

Com $p$ unidades de processamento, $T_1$ da versão sequencial refatorada e
$T_p$ da versão medida:

$$S_p = \frac{T_1}{T_p}, \qquad E_p = \frac{S_p}{p}$$

a fração serial medida de Karp e Flatt (1990):

$$f = \frac{\frac{1}{S_p} - \frac{1}{p}}{1 - \frac{1}{p}}$$

o limite da lei de Amdahl (1967) para essa fração serial:

$$S_{\text{Amdahl}} = \frac{1}{f + \frac{1-f}{p}} \xrightarrow{p \to \infty} \frac{1}{f}$$

e o *speedup* escalado da lei de Gustafson (1988), que supõe o problema crescendo
com o número de processadores (escalabilidade fraca):

$$S'(p) = p - f\,(p-1)$$

$f$ constante indica um limite do programa; $f$ crescendo com $p$ indica custo
de sincronização/comunicação; $f$ irregular indica desbalanceamento de carga.

### Perfil de tempo por worker (`perfis.py`)

O tempo total não diz **onde** o tempo foi. Cada worker cronometra três fases:
**cálculo** (dentro de `calcular_faixa` + `contar_faixa`), **comunicação** (troca
de halo e envio da contagem) e **espera** (barreira na paralela, `DECISAO` na
distribuída). A soma das três deve dar aproximadamente o tempo do laço — a coluna
`soma_sobre_tempo` confere isso (perto de 1,0). O desbalanceamento é
`worker mais lento / média`, então 1,0 é carga perfeitamente dividida.

Na versão paralela a comunicação é **zero** por construção: os processos leem e
escrevem os mesmos blocos de memória compartilhada.

## Medições entre máquinas

`medir.py` mede a versão distribuída **numa máquina só**
(`distribuido/executar_local.py`), onde a rede não é de verdade: o tempo não
inclui a latência de uma rede física. Para medir com duas ou mais máquinas,
suba o coordenador e os *workers* à mão (ver o "Como Executar" do `README.md`
principal) e anote os tempos; esses números entram no relatório como medição
separada, com a topologia descrita.
