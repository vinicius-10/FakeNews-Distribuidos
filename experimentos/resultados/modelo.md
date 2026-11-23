# Efeito das melhorias do modelo

Mesma grade (1000 × 1000, semente 42, 5% de espalhadores iniciais, limiar 2).

| Cenário | Pico de espalhadores | Geração do pico | Alcance final | Alcance vs base | Espalhadores no fim | Gerações até parar |
|---|---|---|---|---|---|---|
| sem melhorias (limiar 2 fixo) | 55,899 | 2 | 57.90% | +0.00 p.p. | 0 | 56 |
| resistência 1–3 (média = base) | 166,385 | 2 | 75.26% | +17.36 p.p. | 0 | 22 |
| resistência 3–5 (mais resistente) | 1,822 | 1 | 5.06% | -52.84 p.p. | 0 | 3 |
| bots 2% | 129,474 | 3 | 93.19% | +35.29 p.p. | 0 | 60 |
| bots 2% + resistência 3–5 | 4,579 | 1 | 7.27% | -50.63 p.p. | 0 | 60 |

**Como ler.** *Alcance* é a fração da população que deixou de ser ignorante. Compare sempre com a primeira linha:

- **resistência 1–3** tem média igual ao limiar da base, mas metade da população passa a precisar de apenas 1 vizinho; o alcance sobe por isso. A heterogeneidade, sozinha, facilita a propagação — não é "mais resistência".
- **resistência 3–5** é o cenário de população mais difícil de convencer (todos acima do limiar da base) e serve para o efeito oposto.
- **bots** nunca deixam de espalhar: a simulação só termina no limite de gerações e os espalhadores humanos zeram enquanto os bots permanecem.