"""As tres figuras do relatorio, como SVG AUTOCONTIDO.

## Por que nao reaproveitar o `graficos.py`

Aquele gera SVG **inline para a pagina do deck**, com as cores vindas de
variaveis CSS (`var(--ink)`) para acompanhar o tema claro/escuro da pagina. Fora
dela, essas variaveis nao resolvem e o grafico sai invisivel.

A submissao da Strategy e um **Kaggle Writeup com galeria de midia**: os
arquivos precisam ser autocontidos. Aqui as cores sao literais.

## As regras de construcao, herdadas e mantidas

  IC sempre visivel onde houver estimativa. Numero sem erro nao e aceito neste
  projeto, e num grafico isso significa a barra, nao so o ponto.

  Legivel em preto e branco: forma e posicao antes de cor.

  Os numeros saem da MESMA fonte das tabelas do texto. Redigitar ja introduziu
  um numero errado uma vez.

Uso:
    python tools/figuras_writeup.py
"""
from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import re
import statistics

RAIZ = pathlib.Path(__file__).resolve().parents[1]
SAIDA = RAIZ / "docs" / "relatorio" / "figuras"

TINTA, FRACO, REGUA = "#1a1a1a", "#6b6b6b", "#d0d0d0"
BOM, RUIM, NEUTRO = "#1a7f4b", "#a4262c", "#4a4a4a"
FUNDO = "#ffffff"

# A submissao da Strategy e em INGLES, e a galeria de midia vai junto com o
# texto. Figura com rotulo em portugues num writeup em ingles e defeito de
# entrega, entao os dois idiomas saem da mesma fonte de numeros.
IDIOMA = "pt"

TEXTOS = {
    "pt": {
        "f0_titulo": "Figura 1 — fluxo de decisão do agente",
        "f0_ent_rot": "entradas",
        "f0_ent": (("estado e ações legais", "recebidos do motor"),
                   ("deck próprio", "60 cartas"),
                   ("catálogo oficial", "1.004 cartas, 1.555 ataques"),
                   ("modelo treinado", "50 pesos, média e desvio")),
        "f0_porta": "primeira chamada do container?",
        "f0_porta_sim": "sim",
        "f0_porta_nao": "não",
        "f0_saida_deck1": "devolve os 60",
        "f0_saida_deck2": "Card IDs do deck",
        "f0_c1a": "busca de um turno",
        "f0_c1b": "determiniza o oculto: embaralha o meu,",
        "f0_c1c": "sorteia o dele pelo uso medido do campo",
        "f0_c1d": "simula cada ação até o fim do turno",
        "f0_c1e": "avalia o estado que resulta de cada uma",
        "f0_aval_rot": "avaliação do estado",
        "f0_aval": ("termos escritos à mão:", "prêmios, nocautes, energia",
                    "+ modelo linear de 50", "variáveis, z = (x − μ) / σ"),
        "f0_c2a": "ordenação heurística",
        "f0_c2b": "escolhe pelo tipo da ação",
        "f0_c3a": "seleção mínima",
        "f0_c3b": "escolhe a primeira ação legal",
        "f0_norma": "select_indices",
        "f0_normb": "ordena por nota e aplica minCount e maxCount",
        "f0_saida1": "seleção legal",
        "f0_saida2": "de índices",
        "f0_gap1": "orçamento de tempo esgotado",
        "f0_gap2": "exceção na camada anterior",
        "f1_titulo": "Figura 2 — trinta rodadas do mesmo agente",
        "f1_sub": "cada ponto é uma rodada de 4.400 partidas; "
                  "a barra é a média do lote",
        "f1_lote_a": "mesmo agente, lote A",
        "f1_lote_b": "mesmo agente, lote B",
        "f1_adotada": "com a alteração adotada",
        "f2_titulo": "Figura 3 — o que sobreviveu ao critério de aceitação",
        "f2_sub": "efeito em pontos percentuais de vitória, "
                  "com intervalo de 95%",
        "f2_fora": "fora da escala: 2 ply −4,9 | premiar dano −7,4 e −11,5",
        "f3_titulo": "Figura 4 — as {n} cartas, por função",
        "f3_sub": "um único atacante básico; o resto é busca, "
                  "energia e disrupção",
    },
    "en": {
        "f0_titulo": "Figure 1 — the agent's decision flow",
        "f0_ent_rot": "inputs",
        "f0_ent": (("state and legal actions", "from the engine"),
                   ("own deck", "60 cards"),
                   ("official catalogue", "1,004 cards, 1,555 attacks"),
                   ("trained model", "50 weights, mean and s.d.")),
        "f0_porta": "first call of the container?",
        "f0_porta_sim": "yes",
        "f0_porta_nao": "no",
        "f0_saida_deck1": "returns the 60",
        "f0_saida_deck2": "deck card IDs",
        "f0_c1a": "one-turn search",
        "f0_c1b": "determinizes the hidden information:",
        "f0_c1c": "his list sampled by measured field use",
        "f0_c1d": "simulates each action to end of turn",
        "f0_c1e": "evaluates the resulting state",
        "f0_aval_rot": "state evaluation",
        "f0_aval": ("hand-written terms:", "prizes, knockouts, energy",
                    "+ linear model, 50", "variables, z = (x − μ) / σ"),
        "f0_c2a": "heuristic ordering",
        "f0_c2b": "chooses by action type",
        "f0_c3a": "minimal selection",
        "f0_c3b": "chooses the first legal action",
        "f0_norma": "select_indices",
        "f0_normb": "ranks by score, applies minCount and maxCount",
        "f0_saida1": "legal selection",
        "f0_saida2": "of indices",
        "f0_gap1": "time budget exhausted",
        "f0_gap2": "exception in the previous layer",
        "f1_titulo": "Figure 2 — thirty rounds of the same agent",
        "f1_sub": "each dot is one round of 4,400 games; "
                  "the bar is the batch mean",
        "f1_lote_a": "same agent, batch A",
        "f1_lote_b": "same agent, batch B",
        "f1_adotada": "with the adopted change",
        "f2_titulo": "Figure 3 — what survived the acceptance criterion",
        "f2_sub": "effect in percentage points of win rate, "
                  "with 95% interval",
        "f2_fora": "off scale: 2 ply -4.9 | rewarding damage -7.4 and -11.5",
        "f3_titulo": "Figure 4 — the {n} cards, by function",
        "f3_sub": "a single basic attacker; the rest is search, "
                  "energy and disruption",
    },
}


def txt(chave: str, **fmt: object) -> str:
    return TEXTOS[IDIOMA][chave].format(**fmt)


def cabeca(w: int, h: int, titulo: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
        f'<rect width="{w}" height="{h}" fill="{FUNDO}"/>',
        f'<text x="16" y="26" font-size="15" font-weight="600" '
        f'fill="{TINTA}">{titulo}</text>',
    ]


def escrever(nome: str, partes: list[str]) -> pathlib.Path:
    SAIDA.mkdir(parents=True, exist_ok=True)
    if IDIOMA != "pt":
        nome = nome.replace(".svg", f"-{IDIOMA}.svg")
    p = SAIDA / nome
    p.write_text("\n".join(partes) + "\n</svg>\n", encoding="utf-8")
    return p


# ------------------------------------------------- Figura 0: arquitetura

# Diagrama de fluxo de analise, nao cartaz. As regras que o desenho segue:
#
#   TRES FAIXAS. Entradas numa banda no topo, processamento numa coluna
#   central, saidas a direita. Quem le sabe onde procurar cada coisa sem
#   seguir seta.
#
#   DOIS PONTOS DE SAIDA, porque o agente tem dois: a primeira chamada do
#   container devolve o DECK e nao uma jogada — contrato que ja custou uma
#   submissao. Esconder isso era o defeito das versoes anteriores.
#
#   O TRILHO DE SUCESSO fica a esquerda e o de falha desce pelo meio. Cada
#   camada sai pelo trilho quando consegue decidir, e desce quando nao
#   consegue; as descidas carregam a condicao. Nenhuma seta cruza outra.
#
#   TUDO PASSA PELO `select_indices`. E verdade no codigo — os tres degraus
#   chamam a mesma funcao — e e o passo que garante o invariante de saida.
#
#   Nenhuma coordenada depende de quanto o texto mede, entao trocar de idioma
#   nao desalinha nada.

COL_X, COL_L = 210, 280              # coluna do processamento
TRILHO_X = 178                       # trilho de sucesso, a esquerda
DIR_X, DIR_L = 510, 174              # faixa da direita: saidas e o detalhe


def _bloco(x, y, larg, alt, titulo, descricoes, numero=None, principal=False,
           mono=False):
    """Retangulo de regua fina com titulo e descricoes alinhados a esquerda."""
    partes = [
        f'<rect x="{x}" y="{y}" width="{larg}" height="{alt}" fill="{FUNDO}" '
        f'stroke="{REGUA}" stroke-width="1"/>'
    ]
    if principal:
        partes.append(f'<rect x="{x}" y="{y}" width="3" height="{alt}" '
                      f'fill="{BOM}"/>')

    texto_x = x + (40 if numero else 14)
    linhas = [(titulo, 12, 600, TINTA)] + [(d, 9.5, 400, FRACO)
                                           for d in descricoes]
    total = sum(tam + 5 for _, tam, _, _ in linhas) - 5
    base = y + (alt - total) / 2 + linhas[0][1] - 2

    if numero:
        partes.append(f'<text x="{x + 16}" y="{base:.1f}" font-size="13" '
                      f'font-weight="600" fill="{FRACO}">{numero}</text>')
    topo = base
    for texto, tam, peso, tinta in linhas:
        fonte = ' font-family="Consolas,monospace"' if (mono and tam == 12) else ''
        partes.append(f'<text x="{texto_x}" y="{topo:.1f}" font-size="{tam}" '
                      f'font-weight="{peso}" fill="{tinta}"{fonte}>{texto}</text>')
        topo += tam + 5
    return partes


def _desce(x, y1, y2, rotulo=""):
    """Descida de um degrau para o seguinte, com a condicao que a provoca."""
    partes = [
        f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2 - 1}" stroke="{FRACO}" '
        f'stroke-width="1"/>',
        f'<path d="M {x - 3.5} {y2 - 6} L {x} {y2} L {x + 3.5} {y2 - 6}" '
        f'fill="none" stroke="{FRACO}" stroke-width="1"/>',
    ]
    if rotulo:
        partes.append(
            f'<text x="{x - 12}" y="{(y1 + y2) / 2 + 4:.1f}" font-size="10" '
            f'fill="{FRACO}" text-anchor="end">{rotulo}</text>')
    return partes


def _saida(y, linha1, linha2, cor):
    """Ponto de saida: seta curta e duas linhas de texto a direita."""
    return [
        f'<line x1="{COL_X + COL_L}" y1="{y}" x2="{DIR_X - 12}" y2="{y}" '
        f'stroke="{cor}" stroke-width="1"/>',
        f'<path d="M {DIR_X - 18} {y - 3.5} L {DIR_X - 12} {y} '
        f'L {DIR_X - 18} {y + 3.5}" fill="none" stroke="{cor}" '
        f'stroke-width="1"/>',
        f'<text x="{DIR_X - 4}" y="{y - 2}" font-size="11.5" '
        f'font-weight="600" fill="{TINTA}">{linha1}</text>',
        f'<text x="{DIR_X - 4}" y="{y + 13}" font-size="11.5" '
        f'font-weight="600" fill="{TINTA}">{linha2}</text>',
    ]


def figura_arquitetura() -> pathlib.Path:
    # Sem titulo embutido: a legenda no documento ja nomeia a figura, e repetir
    # o nome dentro do desenho e ruido. O conteudo sobe 36 px por transform,
    # que e mais seguro que mexer em cada coordenada.
    w, h = 700, 516
    s = cabeca(w, h, "")
    s.append('<g transform="translate(0,-36)">')

    meio = COL_X + COL_L / 2

    # ---------------------------------------------------- faixa de entradas
    ent_y, ent_alt = 62, 46
    s.append(f'<text x="16" y="{ent_y - 6}" font-size="9.5" fill="{FRACO}" '
             f'letter-spacing="1">{txt("f0_ent_rot").upper()}</text>')
    s.append(f'<rect x="16" y="{ent_y}" width="668" height="{ent_alt}" '
             f'fill="{FUNDO}" stroke="{REGUA}" stroke-width="1"/>')
    entradas = TEXTOS[IDIOMA]["f0_ent"]
    celula = 668 / len(entradas)
    for i, (a, b) in enumerate(entradas):
        cx = 16 + celula * i + 14
        if i:
            x_regua = 16 + celula * i
            s.append(f'<line x1="{x_regua:.1f}" y1="{ent_y + 8}" '
                     f'x2="{x_regua:.1f}" y2="{ent_y + ent_alt - 8}" '
                     f'stroke="{REGUA}" stroke-width="1"/>')
        s.append(f'<text x="{cx:.1f}" y="{ent_y + 20}" font-size="10.5" '
                 f'font-weight="600" fill="{TINTA}">{a}</text>')
        s.append(f'<text x="{cx:.1f}" y="{ent_y + 34}" font-size="9.5" '
                 f'fill="{FRACO}">{b}</text>')

    # ------------------------------------------------------------ a porta
    porta_y, porta_alt = 138, 34
    s += _desce(meio, ent_y + ent_alt, porta_y)
    s.append(f'<rect x="{COL_X}" y="{porta_y}" width="{COL_L}" '
             f'height="{porta_alt}" fill="{FUNDO}" stroke="{REGUA}" '
             f'stroke-width="1"/>')
    s.append(f'<text x="{meio}" y="{porta_y + porta_alt / 2 + 4}" '
             f'font-size="11.5" fill="{TINTA}" text-anchor="middle">'
             f'{txt("f0_porta")}</text>')
    s += _saida(porta_y + porta_alt / 2, txt("f0_saida_deck1"),
                txt("f0_saida_deck2"), NEUTRO)
    # alinhado com o texto da saida, e nao centrado na seta: centrado, ele
    # invadia a borda direita da caixa da porta
    s.append(f'<text x="{DIR_X - 4}" y="{porta_y + porta_alt / 2 - 15}" '
             f'font-size="9.5" fill="{FRACO}">{txt("f0_porta_sim")}</text>')

    # ------------------------------------------------------- os tres degraus
    c1_y, c1_alt = 206, 94
    c2_y, c2_alt = 336, 46
    c3_y, c3_alt = 418, 46
    norm_y, norm_alt = 486, 46

    s += _desce(meio, porta_y + porta_alt, c1_y, txt("f0_porta_nao"))
    s += _bloco(COL_X, c1_y, COL_L, c1_alt, txt("f0_c1a"),
                [txt("f0_c1b"), txt("f0_c1c"), txt("f0_c1d"), txt("f0_c1e")],
                numero="1", principal=True)
    s += _bloco(COL_X, c2_y, COL_L, c2_alt, txt("f0_c2a"), [txt("f0_c2b")],
                numero="2")
    s += _bloco(COL_X, c3_y, COL_L, c3_alt, txt("f0_c3a"), [txt("f0_c3b")],
                numero="3")
    s += _desce(meio, c1_y + c1_alt, c2_y, txt("f0_gap1"))
    s += _desce(meio, c2_y + c2_alt, c3_y, txt("f0_gap2"))

    # ------------------------------------- o detalhe da avaliacao, a direita
    s += _bloco(DIR_X, c1_y, DIR_L, c1_alt, txt("f0_aval_rot"),
                list(TEXTOS[IDIOMA]["f0_aval"]))
    liga_y = c1_y + c1_alt / 2
    s.append(f'<line x1="{COL_X + COL_L}" y1="{liga_y}" x2="{DIR_X - 1}" '
             f'y2="{liga_y}" stroke="{REGUA}" stroke-width="1" '
             f'stroke-dasharray="3 3"/>')
    s.append(f'<path d="M {DIR_X - 7} {liga_y - 3.5} L {DIR_X} {liga_y} '
             f'L {DIR_X - 7} {liga_y + 3.5}" fill="none" stroke="{REGUA}" '
             f'stroke-width="1"/>')

    # ------------------------------------------ trilho de sucesso, a esquerda
    centros = (c1_y + c1_alt / 2, c2_y + c2_alt / 2, c3_y + c3_alt / 2)
    norm_meio = norm_y + norm_alt / 2
    s.append(f'<line x1="{TRILHO_X}" y1="{centros[0]}" x2="{TRILHO_X}" '
             f'y2="{norm_meio}" stroke="{BOM}" stroke-width="1"/>')
    for centro in centros:
        s.append(f'<line x1="{COL_X}" y1="{centro}" x2="{TRILHO_X}" '
                 f'y2="{centro}" stroke="{BOM}" stroke-width="1"/>')
        s.append(f'<circle cx="{TRILHO_X}" cy="{centro}" r="2.5" fill="{BOM}"/>')
    s.append(f'<line x1="{TRILHO_X}" y1="{norm_meio}" x2="{COL_X - 1}" '
             f'y2="{norm_meio}" stroke="{BOM}" stroke-width="1"/>')
    s.append(f'<path d="M {COL_X - 7} {norm_meio - 3.5} L {COL_X} {norm_meio} '
             f'L {COL_X - 7} {norm_meio + 3.5}" fill="none" stroke="{BOM}" '
             f'stroke-width="1"/>')

    # ------------------------------------------- normalizacao da saida e fim
    s += _bloco(COL_X, norm_y, COL_L, norm_alt, txt("f0_norma"),
                [txt("f0_normb")], mono=True)
    s += _saida(norm_meio, txt("f0_saida1"), txt("f0_saida2"), BOM)

    s.append('</g>')
    return escrever("fig0-arquitetura.svg", s)


# ------------------------------------------------------- Figura 1: dispersao

def replicas_do_log(nome: str) -> list[float]:
    p = RAIZ / ".runs" / f"{nome}.log"
    if not p.exists():
        return []
    return [float(m) for m in re.findall(
        r"replica\s+\d+\s+atual\s+([\d.]+)%", p.read_text(encoding="utf-8"))]


def figura1() -> pathlib.Path | None:
    """As rodadas do MESMO agente, e o efeito adotado contra esse ruido.

    Tres lotes de dez rodadas. Os dois primeiros sao o MESMO binario medido em
    momentos diferentes — a distancia entre as medias deles e a reprodutibilidade
    da bancada, nao um efeito.
    """
    grupos = [
        (txt("f1_lote_a"), replicas_do_log("t6_ataque75"), NEUTRO),
        (txt("f1_lote_b"), replicas_do_log("t6_ataque50"), NEUTRO),
        (txt("f1_adotada"), replicas_do_log("t7_empata"), BOM),
    ]
    grupos = [g for g in grupos if len(g[1]) >= 3]
    if not grupos:
        return None

    w, h = 700, 300
    x0, x1 = 210, w - 40
    todos = [v for _, vs, _ in grupos for v in vs]
    lo, hi = min(todos) - 0.4, max(todos) + 0.4
    def px(v): return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    s = cabeca(w, h, txt("f1_titulo"))
    s.append(f'<text x="16" y="44" font-size="11" fill="{FRACO}">'
             f'{txt("f1_sub")}</text>')

    # eixo
    ye = h - 42
    s.append(f'<line x1="{x0}" y1="{ye}" x2="{x1}" y2="{ye}" stroke="{REGUA}"/>')
    marca = lo
    while marca <= hi:
        if abs(marca - round(marca * 2) / 2) < 1e-9:
            X = px(marca)
            s.append(f'<line x1="{X:.1f}" y1="{ye}" x2="{X:.1f}" y2="{ye+5}" '
                     f'stroke="{REGUA}"/>')
            s.append(f'<text x="{X:.1f}" y="{ye+19}" font-size="10" '
                     f'fill="{FRACO}" text-anchor="middle">{marca:.1f}%</text>')
        marca += 0.5

    y = 78
    for rot, vs, cor in grupos:
        m, dp = statistics.mean(vs), statistics.stdev(vs)
        s.append(f'<text x="{x0-12}" y="{y+4}" font-size="12" fill="{TINTA}" '
                 f'text-anchor="end">{rot}</text>')
        s.append(f'<text x="{x0-12}" y="{y+18}" font-size="10" fill="{FRACO}" '
                 f'text-anchor="end">{m:.2f}% ± {dp:.2f}pp (n={len(vs)})</text>')
        for v in vs:
            s.append(f'<circle cx="{px(v):.1f}" cy="{y}" r="4" fill="{cor}" '
                     f'fill-opacity="0.45"/>')
        s.append(f'<line x1="{px(m):.1f}" y1="{y-16}" x2="{px(m):.1f}" '
                 f'y2="{y+16}" stroke="{cor}" stroke-width="2.5"/>')
        y += 68
    return escrever("fig1-dispersao.svg", s)


# ----------------------------------------------------- Figura 2: forest plot

# Os efeitos COM intervalo. Os sem IC ficam de fora de proposito: a regra do
# projeto e que numero sem erro nao entra, e num grafico isso e a barra.
# Atualizado em 23/08 com o T8, T9, T10 e T11. A figura mostra o que ficou
# DENTRO da escala do criterio; tres hipoteses caem fora dela e por isso viram
# nota de rodape em vez de barra — 2 ply (-4,9), premiar dano em fracao (-7,4) e
# premiar dano absoluto (-11,5). Espremer a escala para caber -11,5 faria as
# barras de +-1 pp, que sao as que decidem, virarem tracos indistinguiveis.
# (rotulo pt, rotulo en, efeito, limite inferior, limite superior)
EFEITOS = [
    ("Tera Orb 2 -> 4  (adotado)",
     "Tera Orb 2 -> 4  (adopted)", 2.24, 1.79, 2.69),
    ("Night Stretcher 3 -> 1  (adotado)",
     "Night Stretcher 3 -> 1  (adopted)", 1.09, 0.29, 1.89),
    ("Lively Stadium  (adotado)",
     "Lively Stadium  (adopted)", 1.04, 0.06, 2.02),
    ("prioridade de ataque  (adotado)",
     "attack priority  (adopted)", 1.03, 0.21, 1.85),
    ("energia no banco vale menos  (adotado)",
     "bench energy worth less  (adopted)", 0.88, 0.33, 1.43),
    ("vida não paga por rotação  (adotado)",
     "HP no longer pays for rotation  (adopted)", 0.59, 0.09, 1.09),
    ("Hero's Cape  (adotado CONTRA o critério)",
     "Hero's Cape  (adopted AGAINST the criterion)", 0.19, -0.44, 0.82),
    ("quanto a energia do banco desconta",
     "how much bench energy is discounted", 0.19, -0.37, 0.75),
    ("anexar energia acima de jogar carta",
     "attaching energy above playing a card", 0.09, -0.56, 0.74),
    ("regra de Boss's Orders",
     "Boss's Orders rule", 0.09, -1.64, 1.83),
    ("identidade de carta no modelo",
     "card identity in the model", -0.35, -1.76, 1.06),
    ("não-linearidade no modelo",
     "non-linearity in the model", -0.40, -1.83, 1.03),
    ("adotar o consenso do campo (Judge)",
     "adopting the field consensus (Judge)", -2.36, -3.45, -1.26),
]


def figura2() -> pathlib.Path:
    w = 700
    h = 84 + len(EFEITOS) * 30 + 40
    x0, x1 = 300, w - 46
    lo, hi = -4.0, 3.2
    def px(v): return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    s = cabeca(w, h, txt("f2_titulo"))
    s.append(f'<text x="16" y="44" font-size="11" fill="{FRACO}">'
             f'{txt("f2_sub")}</text>')

    zero = px(0)
    s.append(f'<line x1="{zero:.1f}" y1="60" x2="{zero:.1f}" y2="{h-40}" '
             f'stroke="{TINTA}" stroke-dasharray="3 3"/>')
    for marca in (-4, -3, -2, -1, 0, 1, 2, 3):
        X = px(marca)
        s.append(f'<text x="{X:.1f}" y="{h-22}" font-size="10" fill="{FRACO}" '
                 f'text-anchor="middle">{marca:+d}</text>')

    y = 78
    for (rot, rot_en, e, a, b) in EFEITOS:
        rot = rot_en if IDIOMA == "en" else rot
        cor = BOM if a > 0 else RUIM if b < 0 else NEUTRO
        s.append(f'<text x="{x0-12}" y="{y+4}" font-size="11.5" fill="{TINTA}" '
                 f'text-anchor="end">{rot}</text>')
        s.append(f'<line x1="{px(a):.1f}" y1="{y}" x2="{px(b):.1f}" y2="{y}" '
                 f'stroke="{cor}" stroke-width="2"/>')
        for t in (a, b):
            s.append(f'<line x1="{px(t):.1f}" y1="{y-5}" x2="{px(t):.1f}" '
                     f'y2="{y+5}" stroke="{cor}" stroke-width="2"/>')
        s.append(f'<circle cx="{px(e):.1f}" cy="{y}" r="4.5" fill="{cor}"/>')
        y += 30
    s.append(f'<text x="16" y="{h-6}" font-size="10" fill="{FRACO}">'
             f'{txt("f2_fora")}</text>')
    return escrever("fig2-forest.svg", s)


# ------------------------------------------------- Figura 3: as 60 cartas

def figura3(deck: str) -> pathlib.Path | None:
    caminho = RAIZ / deck
    catalogo = RAIZ / "data" / "EN_Card_Data.csv"
    if not (caminho.exists() and catalogo.exists()):
        return None
    tipo = {}
    for r in csv.DictReader(open(catalogo, encoding="utf-8")):
        try:
            tipo.setdefault(int(r["Card ID"]),
                            r.get("Stage (Pokémon)/Type (Energy and Trainer)", "?"))
        except (ValueError, KeyError):
            pass
    ids = [int(x) for x in caminho.read_text(encoding="utf-8").split()
           if x.strip().isdigit()]
    cont = collections.Counter(tipo.get(i, "?") for i in ids)

    ordem = ["Basic Pokémon", "Item", "Supporter", "Stadium",
             "Pokémon Tool", "Special Energy", "Basic Energy"]
    linhas = [(k, cont[k]) for k in ordem if cont.get(k)]
    linhas += [(k, v) for k, v in cont.items() if k not in ordem]

    w = 700
    h = 84 + len(linhas) * 34 + 30
    x0, x1 = 190, w - 60
    maior = max(v for _, v in linhas)

    s = cabeca(w, h, txt("f3_titulo", n=len(ids)))
    s.append(f'<text x="16" y="44" font-size="11" fill="{FRACO}">'
             f'{txt("f3_sub")}</text>')
    y = 76
    for rot, v in linhas:
        larg = (x1 - x0) * v / maior
        cor = BOM if rot == "Basic Pokémon" else NEUTRO
        s.append(f'<text x="{x0-12}" y="{y+13}" font-size="12" fill="{TINTA}" '
                 f'text-anchor="end">{rot}</text>')
        s.append(f'<rect x="{x0}" y="{y}" width="{larg:.1f}" height="18" '
                 f'fill="{cor}" fill-opacity="0.75"/>')
        s.append(f'<text x="{x0+larg+8:.1f}" y="{y+13}" font-size="12" '
                 f'fill="{TINTA}">{v}</text>')
        y += 34
    return escrever("fig3-composicao.svg", s)


def main() -> None:
    global IDIOMA
    ap = argparse.ArgumentParser()
    # O default aponta para o deck EM USO. Ja apontou para um deck antigo, e a
    # figura 3 foi publicada com a composicao errada por isso.
    ap.add_argument("--deck", default="decks/ogerpon_v9.csv")
    ap.add_argument("--idioma", default="pt", choices=sorted(TEXTOS))
    args = ap.parse_args()
    IDIOMA = args.idioma

    for f in (figura_arquitetura(), figura1(), figura2(), figura3(args.deck)):
        if f is None:
            print("  (figura sem dados — pulada)")
        else:
            print(f"  {f.relative_to(RAIZ)}  ({f.stat().st_size/1024:.1f} KB)")


if __name__ == "__main__":
    main()
