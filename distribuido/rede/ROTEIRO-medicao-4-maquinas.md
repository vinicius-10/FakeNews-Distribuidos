# 📏 Medição da distribuída em 4 máquinas (um comando)

Roteiro do dia do teste. A bateria inteira roda sozinha em **~40 min** depois que as 4 máquinas
ligam o agente. Para só conferir a conexão entre máquinas (uma execução, à mão), use o
[`LEIA-ME-3-maquinas.md`](LEIA-ME-3-maquinas.md).

## Quem é quem

| Posição | Máquina | SO | Papel |
|---|---|---|---|
| 0 | notebook do Vinicius (`192.168.0.39`) | Windows | **coordenador** + trabalhador |
| 1 | PC do Rafael | Windows | trabalhador |
| 2 | notebook do Arthur | Windows | trabalhador |
| 3 | notebook do João | Fedora | trabalhador |

A posição é a ordem das faixas, de cima para baixo. Ela fica igual em todas as repetições, e as
faixas de uma mesma máquina ficam juntas: só as bordas entre máquinas passam pela rede. Com
h máquinas, entram as h primeiras posições.

## Antes (cada um na sua máquina)

1. Atualizar a `main` e rodar os testes:
   ```
   git switch main && git pull
   python -m unittest discover -s testes        # Windows (no Linux: python3)
   ```
2. Na tomada, **suspensão e hibernação desligadas**, perfil de desempenho, outros programas
   fechados. Mesma rede (`192.168.0.x`), sem VPN; cabo se der.
3. *Firewall* (já foi configurado no teste anterior; só conferir):
   - Windows: `distribuido\rede\configurar-firewall.ps1` como Administrador;
   - Fedora: `sudo firewall-cmd --zone=trusted --add-source=192.168.0.0/24`.

## No dia

**1. Cada máquina liga o agente** e deixa o terminal aberto até o fim:

```
python -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 1 --ambiente "PC na tomada; cabo"
python -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 2 --ambiente "notebook na tomada; Wi-Fi"
python3 -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 3 --ambiente "notebook na tomada; Wi-Fi"
```

No notebook do Vinicius, num terminal **só para o agente**:

```
python -m distribuido.agente --coordenador 192.168.0.39:5000 --posicao 0 --ambiente "notebook na tomada; Wi-Fi"
```

Use sempre o IP da rede local, inclusive na máquina do coordenador (nunca `127.0.0.1`: o
vizinho usa esse endereço para se conectar). O agente pode ser ligado antes ou depois do
passo 2: ele tenta de novo até o coordenador responder.

**2. No notebook do Vinicius, em outro terminal:**

```
python -m experimentos.medir_rede --maquinas 4 --simular                  # estimativa
python -m experimentos.medir_rede --maquinas 4 --rede "Wi-Fi"
```

O coordenador mostra cada máquina que conectou e a ordem das faixas, e depois roda:

| Fase | O que mede | Tempo |
|---|---|---|
| 1 | sequencial 1000², 2000² e 4000² em **cada** máquina, todas ao mesmo tempo (velocidade de cada uma; mesmo hash em Windows e Linux) | ~16 min |
| 2 | distribuída: 1 a 4 máquinas × 1, 2 ou 4 *workers* por máquina em 1000² e 2000²; 4000² e `--bits` com as 4 | ~23 min |
| 3 | 4 máquinas × 2 *workers*: gerações 10/20/40 e percentual × limiar (cenários do PR #11) | ~4 min |

Parâmetros comuns: 20 gerações, limiar 2, 5%, semente 42, 1 aquecimento + 3 ou 5 repetições.

**3. Fim:** os agentes fecham sozinhos. Os resultados ficam em `experimentos/resultados/rede/`:

| Arquivo | Conteúdo |
|---|---|
| `medicoes.csv` | fases 2 e 3: uma linha por repetição, colunas do `medir.py` + `fase`, `hosts`, `workers_por_host`, `maquinas`, `confere`, `rede` |
| `sequencial_maquinas.csv` | fase 1: sequencial de cada máquina |
| `ambiente_maquinas.csv` | CPU, núcleos, RAM, SO e Python de cada máquina |

`confere = sim` quer dizer que a grade final é igual à da sequencial. Se aparecer
`GRADE DIFERENTE` no terminal, anotar o cenário.

## Se algo der errado

| Sintoma | O que fazer |
|---|---|
| Uma máquina dormiu, caiu a rede, alguém fechou um terminal | ligar o agente de novo e rodar **o mesmo comando** do passo 2: o que já foi medido é pulado |
| O coordenador parou em `Aguardando 4 agente(s)` | falta ligar um agente, ou o IP/porta está errado |
| `conectaram por 127.0.0.1, mas há máquinas de fora` | o agente do Vinicius foi ligado com `127.0.0.1`; usar `192.168.0.39` |
| Uma configuração mostra `FALHOU (...)` | a bateria segue com as outras; rodar de novo no fim refaz só as que faltam |
| Pouco tempo | `--fases 2` (só a rede); a fase 1 e a 3 podem ser rodadas depois com `--fases 1 3` |
