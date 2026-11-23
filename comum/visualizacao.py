"""
Melhoria "visualização gráfica": animação da grade ao longo das gerações.

Gera um único arquivo HTML, sem dependências, que abre em qualquer navegador
(Windows ou Linux) e mostra a grade geração a geração, com botões de
reproduzir/pausar e uma barra para escolher a geração. Fica fora do cálculo:
só lê a grade depois que a geração termina.

Grades grandes são reduzidas por amostragem (uma célula a cada `passo`) para o
arquivo continuar leve.
"""

import json
from pathlib import Path

MODELO_HTML = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Propagação de fake news</title>
<style>
 body{font-family:system-ui,sans-serif;background:#f4f5f3;color:#1c2321;margin:24px}
 canvas{image-rendering:pixelated;border:1px solid #ccc;max-width:100%%}
 .barra{display:flex;gap:12px;align-items:center;margin:12px 0;flex-wrap:wrap}
 .leg span{display:inline-block;width:12px;height:12px;margin:0 4px 0 12px;vertical-align:middle}
</style></head><body>
<h1 style="font-size:20px">Propagação de fake news &mdash; %(titulo)s</h1>
<div class="barra"><button id="play">Reproduzir</button>
<input id="ger" type="range" min="0" max="0" value="0" style="flex:1;min-width:200px">
<span id="rotulo"></span></div>
<canvas id="tela"></canvas>
<p class="leg"><span style="background:#e7ebe9"></span>ignorante<span style="background:#c2410c"></span>espalhador
<span style="background:#5d6865"></span>inativo<span style="background:#6d28d9"></span>bot</p>
<p style="font-size:13px;color:#5d6865">%(nota)s</p>
<script>
const D = %(dados)s;
const CORES = [[231,235,233],[194,65,12],[93,104,101],[109,40,217]];
const tela = document.getElementById("tela"), ctx = tela.getContext("2d");
tela.width = D.colunas; tela.height = D.linhas;
const escala = Math.max(1, Math.floor(600 / Math.max(D.linhas, D.colunas)));
tela.style.width = (D.colunas * escala) + "px";
const img = ctx.createImageData(D.colunas, D.linhas);
const ger = document.getElementById("ger"); ger.max = D.quadros.length - 1;
function mostrar(n) {
  const q = D.quadros[n];
  for (let k = 0; k < q.celulas.length; k++) {
    const c = CORES[q.celulas.charCodeAt(k) - 48];
    img.data[4*k] = c[0]; img.data[4*k+1] = c[1]; img.data[4*k+2] = c[2]; img.data[4*k+3] = 255;
  }
  ctx.putImageData(img, 0, 0);
  document.getElementById("rotulo").textContent = "Geração " + q.geracao;
}
let timer = null;
document.getElementById("play").onclick = () => {
  if (timer) { clearInterval(timer); timer = null; return; }
  timer = setInterval(() => {
    ger.value = (Number(ger.value) + 1) %% D.quadros.length; mostrar(Number(ger.value));
  }, 150);
};
ger.oninput = () => mostrar(Number(ger.value));
mostrar(0);
</script></body></html>
"""


class Animacao:
    """Coleta quadros da grade e grava a animação em HTML."""

    def __init__(self, linhas, colunas, titulo="simulação", lado_maximo=300):
        self.linhas = linhas
        self.colunas = colunas
        self.titulo = titulo
        # Amostragem: uma célula a cada `passo` em cada direção.
        self.passo = max(1, -(-max(linhas, colunas) // lado_maximo))
        self.quadros = []

    def adicionar(self, geracao, plana):
        """Guarda um quadro a partir do vetor com moldura (só leitura)."""
        celulas = []
        for i in range(0, self.linhas, self.passo):
            inicio = (i + 1) * self.colunas
            celulas.extend(plana[inicio + j] for j in range(0, self.colunas, self.passo))
        # Um caractere por célula ('0' a '3') mantém o HTML compacto.
        self.quadros.append({"geracao": geracao, "celulas": bytes(48 + c for c in celulas).decode()})

    def salvar(self, caminho):
        """Grava o arquivo HTML e devolve o caminho."""
        caminho = Path(caminho)
        caminho.parent.mkdir(parents=True, exist_ok=True)
        dados = {"linhas": len(range(0, self.linhas, self.passo)),
                 "colunas": len(range(0, self.colunas, self.passo)),
                 "quadros": self.quadros}
        nota = (f"Grade de {self.linhas} x {self.colunas}"
                + (f", mostrada com 1 célula a cada {self.passo}." if self.passo > 1 else "."))
        with open(caminho, "w", encoding="utf-8") as arquivo:
            arquivo.write(MODELO_HTML % {"titulo": self.titulo, "nota": nota,
                                         "dados": json.dumps(dados)})
        return caminho
