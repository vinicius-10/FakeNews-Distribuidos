# 🤝 Como Contribuir

> Regras combinadas pelo grupo para trabalhar no projeto. Valem para todos, com ou sem ajuda de IA.
> Leia antes do primeiro *pull request* (PR).

## 📑 Sumário

- [Regras do enunciado](#-regras-do-enunciado-não-negociáveis)
- [Ambiente](#-ambiente)
- [Código compatível com Windows e Linux](#-código-compatível-com-windows-e-linux)
- [Fluxo de trabalho com Git](#-fluxo-de-trabalho-com-git)
- [Commits](#-commits)
- [Pull requests e revisão](#-pull-requests-e-revisão)
- [Testes](#-testes)
- [Estilo de código](#-estilo-de-código)
- [Experimentos e medições](#-experimentos-e-medições)
- [Relatório](#-relatório)
- [Uso de IA e referências](#-uso-de-ia-e-referências)

---

## 🚫 Regras do enunciado (não negociáveis)

Violar qualquer uma delas compromete a nota do trabalho inteiro.

1. **Nada de paralelismo implícito** no cálculo da próxima geração: proibido NumPy vetorizado,
   Pandas, Numba, Cython, GPU/CUDA e *frameworks* paralelos. A divisão do trabalho, a
   sincronização e a comunicação são escritas à mão (`threading`, `multiprocessing`, `socket`).
   Bibliotecas como `matplotlib` só podem ser usadas **fora** da simulação (gráficos, análise).
2. **Mesmo resultado lógico da versão sequencial.** A grade inicial é gerada uma única vez, pelo
   processo principal, com `criar_grade(..., semente=42)`, e só depois dividida entre os
   *workers*. Nenhum *worker* sorteia nada por conta própria. A transição é determinística, então
   as três versões devem produzir exatamente a mesma grade em toda geração.
3. **Referenciar toda ajuda externa:** IA, código de terceiros, artigos e bibliotecas (ver
   [Uso de IA e referências](#-uso-de-ia-e-referências)).
4. **Todos precisam entender todo o código**, porque todos explicam partes dele no vídeo. Código
   claro e comentado vale mais que código "esperto".

O código do professor (`sequencial/fakenews_sequencial_original.py`) é a referência de
comportamento e **não deve ser alterado**: refatorações vão em outro arquivo.

## 💻 Ambiente

O grupo usa **Windows 11** e **Linux**. Tudo no repositório deve rodar **nativo nos dois**, com o
mesmo comando. O WSL é opcional (útil para reproduzir um problema do Linux no Windows), nunca
requisito.

- **Python 3.12** em todas as máquinas, para que todos tenham o mesmo comportamento.
- A simulação usa só a biblioteca padrão.

| Ação | Windows (PowerShell) | Linux |
|---|---|---|
| Rodar o Python | `py` ou `python` | `python3` |
| Criar o ambiente virtual | `py -3.12 -m venv .venv` | `python3.12 -m venv .venv` |
| Ativar o ambiente virtual | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |

Com o ambiente virtual ativo, `python` funciona igual nos dois.

## 🐧🪟 Código compatível com Windows e Linux

### `multiprocessing`: sempre *spawn*

No Linux, o padrão do Python 3.12 é criar processos por **fork**: o filho nasce como cópia do
pai, com todas as variáveis já preenchidas. No Windows só existe o **spawn**: o filho começa um
interpretador novo, **importa o módulo de novo** e recebe os argumentos serializados (*pickle*).
Código que funciona com fork pode quebrar com spawn, por exemplo:

- criar processos fora do `if __name__ == "__main__":` (no Windows, cada filho criaria filhos de
  novo, e o Python aborta com `RuntimeError`);
- usar uma variável global alterada pelo pai depois do *import* (o filho não a vê);
- passar uma `lambda` ou uma função aninhada como alvo (não é serializável).

Por isso usamos **spawn explícito nos dois sistemas**: quem desenvolve no Linux enxerga os mesmos
erros de quem está no Windows.

```python
import multiprocessing as mp


def trabalhador(id_worker, faixa, fila):   # função no nível do módulo (serializável)
    ...


def main():
    ctx = mp.get_context("spawn")           # mesmo comportamento no Windows e no Linux
    fila = ctx.Queue()
    processos = [ctx.Process(target=trabalhador, args=(i, faixa, fila))
                 for i, faixa in enumerate(faixas)]
    ...


if __name__ == "__main__":
    main()
```

Criar um processo custa caro, principalmente no Windows (centenas de milissegundos). Os
*workers* são criados **uma vez** e reutilizados em todas as gerações, nunca recriados a cada
geração.

### Arquivos e caminhos

- Use `pathlib` e caminhos relativos ao próprio arquivo, por exemplo
  `Path(__file__).resolve().parent / "resultados"`. Nunca escreva `\` nem `C:\` no código.
- Sempre `open(..., encoding="utf-8")`: o padrão do Windows é cp1252 e quebra os acentos. Em CSV,
  também `newline=""`.
- O Linux diferencia maiúsculas de minúsculas: o nome do arquivo e o do `import` precisam ser
  idênticos.

### Sockets (versão distribuída)

- Host e porta sempre por argumento de linha de comando, com padrão `127.0.0.1`. Use portas acima
  de 1024 e porta `0` nos testes, para o sistema escolher uma livre.
- Não use `SO_REUSEADDR`: no Windows ele deixa outro processo usar a mesma porta.
- Toda espera tem *timeout*, para que um erro vire mensagem e não um programa travado.
- `recv` pode devolver **parte** de uma mensagem nos dois sistemas. Cada mensagem leva o tamanho
  no início (por exemplo, 4 bytes com `struct.pack("!I", n)`): envie com `sendall` e leia em laço
  até completar.
- No Windows, o *firewall* pergunta na primeira execução: permita o Python em **rede privada**.
  Para testar entre computadores, todos na mesma rede e o servidor escutando em `0.0.0.0`.

### O que não usar

Nada exclusivo de um sistema: `os.fork`, `fcntl`, `resource`, `signal.SIGALRM`, `select` em
*pipes* ou arquivos, `msvcrt`, `winreg`. Scripts de execução e de experimentos são escritos em
**Python** (`python -m ...`), não em `.sh` ou `.ps1`.

Os finais de linha ficam por conta do Git: o `.gitattributes` grava tudo com LF. O
`.editorconfig` configura os editores (UTF-8, LF, 4 espaços no Python).

## 🌿 Fluxo de trabalho com Git

Usamos o **GitHub Flow**: a `main` sempre funciona, e cada trabalho novo tem sua própria *branch*.

1. **Começar:** atualize a `main` e crie a *branch* antes de editar qualquer arquivo.
   ```bash
   git switch main
   git pull
   git switch -c tipo/assunto
   ```
   O nome segue os tipos dos commits, em minúsculas, sem acento e com hífens: `feat/versao-paralela`,
   `feat/distribuida-sockets`, `fix/troca-de-bordas`, `test/equivalencia`, `docs/readme-execucao`.
   Antes, confira em `git branch -r` e na aba *Pull requests* se alguém já está no mesmo assunto.
2. **Trabalhar:** faça commits pequenos e envie com frequência (`git push -u origin tipo/assunto`
   na primeira vez, depois só `git push`). Nada fica só no seu computador.
3. **Manter atualizada:** quando a `main` andar, traga-a para a sua *branch* com
   `git fetch` e `git merge origin/main`. Use merge, não rebase.
4. **Abrir o PR** para a `main` quando a parte estiver pronta (seção seguinte).
5. **Merge** depois de 1 aprovação, com **merge commit**. A *branch* é apagada em seguida.

**Exceção:** a sincronização do relatório com o Overleaf (`docs(relatorio): ...`) vai direto na
`main`.

**Nunca:** `git push --force`, rebase de *branch* já enviada, commit direto na `main` (fora a
exceção), nem commit na *branch* de outra pessoa sem combinar com ela.

## 📝 Commits

Seguimos o [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/), com o texto
em português:

```text
tipo(escopo): resumo em minúsculas, sem ponto final

Corpo opcional: o que mudou e por quê, e o resultado dos testes.
```

| Tipo | Quando |
|---|---|
| `feat` | funcionalidade nova (versão, melhoria do modelo, opção de linha de comando, script) |
| `fix` | correção de bug (resultado divergente, *deadlock*, troca de bordas errada) |
| `perf` | ganho de desempenho sem mudar o resultado |
| `refactor` | reorganização sem mudar o comportamento |
| `test` | só testes |
| `docs` | README, comentários, relatório |
| `build` / `chore` | scripts de execução, configuração, `.gitignore` |

**Escopos:** `sequencial`, `paralelo`, `distribuido`, `comum`, `protocolo`, `testes`,
`experimentos`, `resultados`, `relatorio`, `slides` e o nome da melhoria (`influenciadores`,
`bots`...).

Exemplo: `feat(paralelo): divide a grade em faixas de linhas entre processos`.

## 🔍 Pull requests e revisão

- O título do PR segue o padrão dos commits. A descrição segue o modelo que aparece
  automaticamente: o que muda, como foi testado, o que olhar na revisão e o uso de IA.
- O PR precisa de **1 aprovação** de outro integrante. Qualquer integrante pode fazer o merge
  depois da aprovação, usando **merge commit**.
- Sempre que possível, quem revisa usa um sistema operacional diferente do de quem escreveu: os
  testes rodados na revisão já conferem a compatibilidade.
- A revisão também serve para estudar: quem revisa uma parte fica sabendo explicá-la no vídeo.

**Checklist de revisão:**

- [ ] Resultado idêntico ao da sequencial (testes de equivalência passando).
- [ ] Sem paralelismo implícito no cálculo da geração.
- [ ] Sem condição de corrida: grade da geração atual só lida, grade da próxima só escrita
      (*buffer* duplo), barreira entre gerações, bordas (*halo*) atualizadas antes do cálculo.
- [ ] Roda no Windows e no Linux (*spawn*, `__main__`, `pathlib`, `utf-8`).
- [ ] Código claro, com comentários explicando o porquê.
- [ ] README (Andamento, Como Executar) e referências atualizados.

## 🧪 Testes

- Os testes ficam em `testes/` e rodam com
  `python -m unittest discover -s testes -v` (56 testes, ~15 s). Só a biblioteca padrão, para
  funcionar igual em todas as máquinas. A lista de arquivos e o que cada um cobre está no README.
- **Teste de equivalência:** as três versões, com grades pequenas e vários cenários (tamanhos,
  limiar, número de *workers*, divisão não exata das linhas), comparadas geração a geração com a
  sequencial.
- **Robustez da distribuída** (`test_robustez.py`): *workers* reais em *threads* e *workers*
  falsos simulam conexões estranhas e falhas; toda espera tem que terminar em erro com contexto,
  nunca travar.
- **Teste primeiro** em correção de defeito: o teste novo falha antes da correção pelo motivo
  esperado e passa depois.
- Os testes rodam antes de abrir o PR, e o resultado vai na descrição.
- Quem mexer em processos, sockets ou arquivos roda os testes nos dois sistemas, ou pede que o
  revisor rode no outro.

## 🎨 Estilo de código

- [PEP 8](https://peps.python.org/pep-0008/), com 4 espaços de indentação.
- Nomes de funções e variáveis em **português** e `snake_case`, como no código do professor
  (`criar_grade`, `proxima_geracao`). Comentários e *docstrings* também em português.
- Toda função tem uma *docstring* curta. Comentários explicam o **porquê** (por que a barreira
  está ali, por que a cópia é necessária), não repetem o que a linha faz.
- O que as três versões compartilham (regras do autômato, criação da grade, leitura de
  parâmetros) fica em `comum/`, sem duplicar código. Mudanças em `comum/` vão em PRs pequenos,
  avisando o grupo, porque afetam todo mundo.
- Parâmetros (tamanho, gerações, percentual de espalhadores, limiar, *workers*, host e porta)
  vêm da linha de comando (`argparse`), não de valores fixos no código.

## 📊 Experimentos e medições

- Cada gráfico de *speedup* usa execuções de **uma única máquina e um único sistema
  operacional**. Não misture computadores nem Windows com Linux no mesmo gráfico.
- O script de medição grava a configuração da máquina: CPU, núcleos físicos e lógicos, RAM,
  sistema operacional e versão do Python.
- Faça 1 execução de aquecimento descartada e pelo menos 5 repetições, e reporte a mediana.
  Durante a medição, notebook na tomada e outros programas fechados.
- Os resultados ficam em CSV em `experimentos/resultados/`, e os gráficos são gerados por script,
  nunca editados à mão.
- Com limiar 3, a simulação morre em cerca de 3 gerações. Os *benchmarks* usam limiar 2 ou
  desligam a parada antecipada.

## 📄 Relatório

- O relatório é escrito no **Overleaf** da UTFPR (fonte oficial). A pasta `relatorio/` é só uma
  cópia para versionamento: **não edite lá**, porque a próxima sincronização sobrescreve.
- Normas ABNT adotadas pela UTFPR (referências pela NBR 6023:2018). No texto, escreva "Seção"
  (não "Capítulo").

## 🤖 Uso de IA e referências

O enunciado exige referenciar **toda** ajuda externa.

- **IA:** commits feitos com ajuda de IA levam a linha
  `Co-Authored-By: <ferramenta> <e-mail>`. O PR diz, na seção "Uso de IA", o que foi feito com
  ajuda, e o relatório cita as ferramentas usadas.
- **Código de terceiros:** comentário acima do trecho com a origem (link) e a licença.
- **Artigos, livros e documentação:** entram no `main.bib` do relatório quando embasam uma
  decisão (por exemplo, uma melhoria ou o protocolo).
