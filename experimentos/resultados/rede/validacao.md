# Validação — 23/nov/2026

Registro dos testes rodados na máquina do grupo (PC Windows, 192.168.0.4) antes de levar o código
aos notebooks do teste entre máquinas.

## Ambiente

| Item | Valor |
|---|---|
| Máquina | PC do grupo (`pc-rafa`), Windows 10 (10.0.26300) |
| CPU | 16 núcleos físicos / 24 lógicos |
| RAM | 31,8 GB |
| Python | 3.11.7 (padrão) e 3.12.10 (o dos notebooks) |
| Rede | Ethernet `192.168.0.4/24`, perfil **Private** |

## 1. Suíte de testes

```
python    -m unittest discover -s testes   ->  Ran 27 tests ... OK
py -3.12  -m unittest discover -s testes   ->  Ran 27 tests ... OK
```

Cobre: núcleo igual ao professor, conversões e faixas, borda em bits, melhorias do modelo,
protocolo (mensagens grandes, vazias, conexão fechada no meio, tipo errado) e equivalência das quatro
versões geração a geração.

## 2. Equivalência das versões

Cenário padrão do professor (100×100, 50 gerações, 5%, limiar 3) — a simulação morre na geração 3:

| versão | ignorantes | espalhadores | inativos |
|---|---|---|---|
| sequencial | 9.463 | 0 | 537 |
| paralela processos ×4 | 9.463 | 0 | 537 |
| paralela threads ×4 | 9.463 | 0 | 537 |
| distribuída local ×3 | 9.463 | 0 | 537 |

Cenário longo (100×100, limiar 2, 26 gerações):

| versão | ignorantes | espalhadores | inativos |
|---|---|---|---|
| sequencial | 5.532 | 0 | 4.468 |
| distribuída ×3 `--bits` | 5.532 | 0 | 4.468 |

## 3. Distribuída pela interface de rede real

Estes usam `--host 0.0.0.0` e workers conectando em `192.168.0.4` — o mesmo caminho TCP de um teste
entre máquinas. O `executar_local` usa `127.0.0.1`, que o Windows isenta do firewall e daria falso
positivo.

| cenário | ignorantes | espalhadores | inativos | tempo do laço | tempo total |
|---|---|---|---|---|---|
| 2 workers, 500×500, 20 ger, limiar 2 | 108.188 | 855 | 140.957 | 0,55 s | 0,99 s |
| 3 workers, 800×800, 25 ger, limiar 2 | 272.616 | 880 | 366.504 | 1,12 s | 1,77 s |

Sequencial de referência nos mesmos cenários: **108.188 / 855 / 140.957** e **272.616 / 880 / 366.504** —
idênticos.

## 4. Pacote portátil

ZIP extraído em pasta limpa, rodado com Python 3.12:

- 27 testes OK;
- `python -m distribuido.executar_local --workers 3 --linhas 200 --colunas 200 --geracoes 10 --limiar 2`
  → `21.377 / 941 / 17.682`.

## Pendências (dependem dos notebooks)

1. Liberar o firewall do PC no perfil `Private` (`distribuido/rede/configurar-firewall.ps1`, como
   Administrador). Sem isso o worker conecta na porta 5000 e o halo morre em silêncio.
2. Preparar os dois notebooks: Python 3.12 + `FakeNews-distribuido.zip` + suíte OK.
3. Rodar com as 3 máquinas reais e comparar com a sequencial.
4. Medir tempo e preencher a tabela de cenários para o capítulo de experimentos.
