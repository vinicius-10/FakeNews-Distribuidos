# Relatório técnico — Sistemas Distribuídos (UTFPR)

Relatório do trabalho final de Sistemas Distribuídos, escrito no modelo LaTeX da UTFPR
(classe `utfpr.cls` v3.0, baseada no [abnTeX2](https://www.abntex.net.br/)).

## Como compilar

- **Overleaf:** compilador **pdfLaTeX**, TeX Live mais recente (testado no TeX Live 2026).
- **Local:** pdfLaTeX + BibTeX + makeglossaries/makeindex (ex.: `latexmk -pdf main.tex`).
  Testado também no **TeX Live 2021**, com o mesmo resultado do Overleaf.
- Não é mais preciso escolher "TeX Live 2021 (Legacy)" no Overleaf: essa orientação antiga do
  modelo não vale para esta versão (ver "Mudanças em relação ao modelo").

## Estrutura

| Arquivo/pasta | Conteúdo |
|---|---|
| `main.tex` | estrutura do documento (ordem dos elementos) |
| `variaveis.tex` | dados da capa e da folha de rosto, palavras-chave, licença |
| `configuracoes.tex` | pacotes e comandos adicionais (`\todo`, listagens de código, `\caixa`) |
| `utfpr.cls` | classe do modelo (formatação ABNT/UTFPR) — evite editar |
| `capitulos/` | seções do relatório (uma por arquivo) |
| `PreTexto/` | resumo, abstract, lista de siglas (`lista-acronimos.tex`) |
| `PosTexto/` | apêndices |
| `figuras/` | imagens das figuras (`\includegraphics{nome}`) |
| `main.bib` | referências (BibTeX, estilo `abntex2-alf.bst`) |

Convenções: siglas com `\ac{SIGLA}` (só as usadas entram na lista); fonte de figura/tabela com
`\fonte{}` (vazio = "Autoria própria (ano)"); remissão a seções com `Seção~\ref{...}`.

## Mudanças em relação ao modelo UTFPR v3.0

- **Compatibilidade com o TeX Live 2021:** a v3.0 aplicava `\xmakefirstuc` às seções no sumário;
  com o `mfirstuc` do TeX Live 2021 o sumário não compilava (`Incomplete \iffalse`). Removido —
  a capitalização não tinha efeito, pois o número vem antes do título.
- **Sumário dos apêndices:** a seção secundária saía colada ao travessão ("A.1–Título"); corrigido
  para "A.1 Título".
- `\settocpreprocessor` (obsoleto no memoir) removido da classe: a caixa alta dos capítulos no
  sumário já vem do abnTeX2.
- Capa sem âncora de página e contagem a partir da folha de rosto (eliminava âncora duplicada).
- Siglas, glossário e símbolos: `\usepackage[printonlyused]{acronym}`; entradas de exemplo de
  glossário removidas; `\input` no preâmbulo no lugar de `\include`.
- Idiomas: `brazilian` (nome atual no babel) e `english`; `french`/`spanish` removidos.
- `subfig` (sem manutenção desde 2005), `lipsum` e definições duplicadas removidos.
- Removidos os arquivos de exemplo do modelo (capítulos, figuras, apêndices, logos de outros
  programas, folha de aprovação) e os elementos de TCC que não se aplicam (dedicatória,
  agradecimentos, epígrafe, errata, banca). Ficam recuperáveis pelo histórico do Overleaf.

## Avisos esperados na compilação

Vêm de pacotes do TeX Live ou de decisões do modelo e não indicam erro:

- `Name 'brazil' is deprecated` e `\settocpreprocessor is marked deprecated` — vêm do `abntex2.cls`.
- `No 'datatool' support for dialect 'brazilian'` — o `datatool` não tem módulo para português.
- `The titlesec package is not recommended with memoir` — o modelo usa o `titlesec` para a seção
  quaternária no padrão UTFPR (sem recuo, só o título sublinhado).
- `Option 'pdftex' has already been used` e `Setting all color commands to rgb` — do `pdfx` (PDF/A).
- `Underfull \hbox` — linhas justificadas com espaço sobrando; revisar só se ficar visível.

## Normas adotadas pela UTFPR

NBR 14724:2024 (trabalhos acadêmicos), NBR 10520:2023 (citações), NBR 6023:2018 (referências),
NBR 6024:2012 (numeração das seções), NBR 6027:2012 (sumário), NBR 6028:2021 (resumo),
NBR 6034:2004 (índice), NBR 15287:2025 (projeto de pesquisa). Fonte: página "Trabalhos
acadêmicos" das Bibliotecas UTFPR.

## Créditos do modelo

Modelo LaTeX da UTFPR, baseado no abnTeX2 e nos modelos `utfprpgtex.cls` (Luiz E. M. Lima) e
`Monografia-utfpr-dagro-nov2019.cls` (Jorge Jamhour). Mantido por Vinicius Pegorini, com
atualizações de Marco Aurélio Graciotto Silva, Rogério Aparecido Gonçalves, Luiz Arthur Feitosa
dos Santos (v2.5, 2022) e Silvio Sanches (v3.0, 2025). Os mantenedores informam que o modelo é um
facilitador, sem vínculo com a biblioteca ou com a ABNT, e que é usado por conta e risco de quem o
utiliza; as regras oficiais são as da ABNT e da biblioteca da UTFPR.
