"""Treina a regressao logistica e injeta os coeficientes no submission/main.py.

Por que logistica e nao o gradient boosting, que acerta 2,6pp a mais: o modelo
precisa ir DENTRO do pacote. A logistica sao ~47 floats como constante; 300
arvores nao cabem, e o arquivo ja me pregou uma peca de empacotamento hoje.
Se a logistica passar no painel, ai vale destilar o GBM.

As features vem de `main.features_da_decisao` — a mesma funcao que a inferencia
usa. Nao ha extrator de treino separado, de proposito.

Uso:
    python tools/exportar_prior.py
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import pathlib
import sys
import textwrap

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "submission"))
sys.path.insert(0, str(RAIZ / "engine"))
sys.path.insert(0, str(RAIZ / "tools"))

import main as agente  # noqa: E402

INICIO = "# <<< PRIOR_INICIO"
FIM = "# >>> PRIOR_FIM"
TAXA_INICIO = "# <<< TAXA_INICIO"
TAXA_FIM = "# >>> TAXA_FIM"


def carregar():
    linhas = []
    for f in sorted(glob.glob(str(RAIZ / "data" / "analise" / "imitacao_*.csv"))):
        linhas += list(csv.DictReader(open(f, encoding="utf-8")))
    return linhas


SUAVIZACAO = 50.0   # ofertas de peso; PRE-DEFINIDO, nao varrido


def _cid(linha) -> int:
    try:
        return int(float(linha.get("carta_id", -1)))
    except (TypeError, ValueError):
        return -1


def taxa_das_cartas(treino: list[dict]) -> tuple[dict[int, float], float]:
    """cardId -> taxa suavizada de escolha quando oferecida. SO DO TREINO.

    Codificacao por alvo calculada sobre o conjunto inteiro vaza o rotulo e
    infla a metrica — e o erro classico desta tecnica. A tabela sai daqui com
    as linhas de TREINO e e aplicada ao teste sem que ele contribua.

    Suavizacao aditiva com `SUAVIZACAO` ofertas de peso na media global, para
    que uma carta vista tres vezes nao entre com taxa 1,0 ou 0,0.
    """
    ofertas: collections.Counter = collections.Counter()
    escolhas: collections.Counter = collections.Counter()
    for l in treino:
        c = _cid(l)
        if c < 0:
            continue
        ofertas[c] += 1
        escolhas[c] += int(l["escolhida"])
    total = sum(ofertas.values())
    if not total:
        return {}, 0.0
    media = sum(escolhas.values()) / total
    tabela = {c: (escolhas[c] + SUAVIZACAO * media) / (n + SUAVIZACAO)
              for c, n in ofertas.items()}
    return tabela, media


def matriz(linhas, tabela: dict[int, float], padrao: float):
    nomes = agente.NOMES_FEATURES

    def valor(l, c):
        # `taxa_da_carta` e DERIVADA, nao coletada: o CSV traz `carta_id` e a
        # tabela vem do treino. Assim a disciplina do split mora num lugar so.
        if c == "taxa_da_carta":
            return tabela.get(_cid(l), padrao)
        return float(l[c])

    X = np.array([[valor(l, c) for c in nomes] for l in linhas],
                 dtype=np.float64)
    y = np.array([int(l["escolhida"]) for l in linhas], dtype=np.int8)
    g = np.array([f'{l["episodio"]}|{l["passo"]}' for l in linhas])
    return X, y, g


def top1(scores, grupo, y):
    por: dict = collections.defaultdict(list)
    for i, k in enumerate(grupo):
        por[k].append(i)
    ok = sum(int(y[max(idx, key=lambda i: scores[i])] == 1) for idx in por.values())
    return ok / max(len(por), 1), len(por)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", type=float, default=0.25)
    args = ap.parse_args()

    linhas = carregar()
    if not linhas:
        raise SystemExit("sem dados — rode tools/coletar_imitacao.py")

    # SPLIT POR EPISODIO: decisoes da mesma partida sao correlacionadas
    eps = sorted({l["episodio"] for l in linhas})
    rng = np.random.default_rng(20260810)
    rng.shuffle(eps)
    treino = set(eps[:int(len(eps) * (1 - args.teste))])
    tr = [l for l in linhas if l["episodio"] in treino]
    te = [l for l in linhas if l["episodio"] not in treino]

    tabela, media = taxa_das_cartas(tr)
    if not tabela:
        print("AVISO: nenhum `carta_id` nos dados — `taxa_da_carta` fica"
              " constante.\n       Recolete com o tools/coletar_imitacao.py"
              " atualizado.\n")
    Xtr, ytr, _ = matriz(tr, tabela, media)
    Xte, yte, gte = matriz(te, tabela, media)
    print(f"{len(linhas)} linhas | {len(eps)} episodios "
          f"({len(treino)} treino / {len(eps)-len(treino)} teste)")
    print(f"  {len(agente.NOMES_FEATURES)} features, do proprio main.py\n")

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    esc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(max_iter=2000, C=1.0)
    lr.fit(esc.transform(Xtr), ytr)

    por = collections.Counter(gte)
    acaso = sum(1 / n for n in por.values()) / len(por)
    l0 = np.array([agente.BASE_PRIORITY.get(
        next((t for t in range(17) if l[f"tipo_{t}"] == "1.0"), -1),
        agente.OTHER_PRIORITY) - 0.001 * float(l["indice"]) for l in te])
    p_l0, n_dec = top1(l0, gte, yte)
    p_lr, _ = top1(lr.decision_function(esc.transform(Xte)), gte, yte)

    # A REGRA TRIVIAL: sempre a primeira opcao da lista. Ela faltava aqui, e a
    # falta escondeu o resultado central de 18/08 — o prior EMPATA com ela
    # (+0,05 pp, IC [-0,78; +0,88]), porque a feature `indice` pesa 9,4x a
    # segunda e o modelo nao discrimina DENTRO do tipo. Comparar so com a L0 e
    # com o acaso deixa passar um modelo que nao aprendeu nada alem da ordem.
    # Ver docs/prior-contra-regra-trivial-2026-08-18.md.
    p_triv, _ = top1(np.array([-float(l["indice"]) for l in te]), gte, yte)

    # A ABLACAO que decide se a feature nova paga: o MESMO pipeline, os MESMOS
    # dados, so sem `taxa_da_carta`. Comparar contra o prior antigo seria
    # comparar tambem os dados, que mudaram — e ai nao se sabe qual dos dois
    # moveu o numero.
    nomes = list(agente.NOMES_FEATURES)
    if "taxa_da_carta" in nomes:
        idx = [i for i, c in enumerate(nomes) if c != "taxa_da_carta"]
        esc_s = StandardScaler().fit(Xtr[:, idx])
        lr_s = LogisticRegression(max_iter=2000, C=1.0)
        lr_s.fit(esc_s.transform(Xtr[:, idx]), ytr)
        p_sem, _ = top1(lr_s.decision_function(esc_s.transform(Xte[:, idx])),
                        gte, yte)
    else:
        p_sem = None

    print(f"  {'acaso':24}{100*acaso:6.1f}%")
    print(f"  {'heuristica L0':24}{100*p_l0:6.1f}%")
    print(f"  {'TRIVIAL: sempre a 1a':24}{100*p_triv:6.1f}%")
    if p_sem is not None:
        print(f"  {'logistica SEM taxa_carta':24}{100*p_sem:6.1f}%")
    print(f"  {'logistica (exportada)':24}{100*p_lr:6.1f}%"
          f"   {100*(p_lr-p_l0):+.1f}pp sobre a L0"
          f"   {100*(p_lr-p_triv):+.1f}pp sobre a TRIVIAL")
    if p_sem is not None:
        import estatistica as est
        d, lo, hi = est.diferenca_de_proporcoes(
            round(p_lr * n_dec), n_dec, round(p_sem * n_dec), n_dec)
        print(f"\n  o que `taxa_da_carta` acrescenta: {100*d:+.2f} pp"
              f"  IC [{100*lo:+.2f}; {100*hi:+.2f}]  (Newcombe)")
        d2, lo2, hi2 = est.diferenca_de_proporcoes(
            round(p_lr * n_dec), n_dec, round(p_triv * n_dec), n_dec)
        print(f"  o modelo sobre a REGRA TRIVIAL:  {100*d2:+.2f} pp"
              f"  IC [{100*lo2:+.2f}; {100*hi2:+.2f}]")

    if p_lr <= p_triv:
        print("\n  ATENCAO: o modelo NAO bate a regra trivial. Isso nao bloqueia"
              "\n  a exportacao — quem decide e o painel — mas nao apresente o"
              "\n  resultado como 'avaliacao aprendida' sem dizer isto.")
    print(f"\n  {n_dec} decisoes no teste\n")

    def lit(vals):
        txt = ", ".join(f"{v:.6g}" for v in vals)
        return textwrap.fill(txt, width=74, initial_indent="    ",
                             subsequent_indent="    ")

    corpo = f"""{INICIO}
# Prior de politica — GERADO por tools/exportar_prior.py, NAO EDITAR A MAO.
#
# Regressao logistica sobre {len(agente.NOMES_FEATURES)} features, treinada em
# {len(tr):,} linhas de {len(treino)} episodios da ladder com professor de rating
# ~1.100. Split por EPISODIO; top-1 no teste: {100*p_lr:.1f}% contra {100*p_l0:.1f}%
# da heuristica L0, {100*p_triv:.1f}% da regra TRIVIAL ("sempre a primeira opcao
# da lista") e {100*acaso:.1f}% do acaso, em {n_dec} decisoes.
#
# A trivial e a linha de base que importa, e ela faltava ate 18/08: a feature
# `indice` pesa ~9x a segunda, e o modelo NAO discrimina dentro de um mesmo
# tipo de jogada. O valor dele esta em atravessar fronteiras de TIPO — que e
# onde os +10,11pp do painel foram medidos.
# Ver docs/prior-contra-regra-trivial-2026-08-18.md.
#
# Vai como constante e nao como arquivo separado: o import dependeria do
# diretorio do pacote estar no sys.path do container, que e a mesma aposta do
# `__file__` — e aquela custou tres submissoes.
PRIOR_PESOS = (
{lit(lr.coef_[0])}
)
PRIOR_MEDIA = (
{lit(esc.mean_)}
)
PRIOR_DESVIO = (
{lit(np.sqrt(esc.var_))}
)
PRIOR_VIES = {lr.intercept_[0]:.6g}
{FIM}""".replace(",", ",")

    # A TABELA de taxa por carta vai junto, e no MESMO passo: ela e parte do
    # modelo. Exportar os pesos sem ela deixaria a feature constante e o peso
    # dela sem sentido — e a divergencia so apareceria no painel, tarde.
    itens = ", ".join(f"{c}: {t:.5g}" for c, t in sorted(tabela.items()))
    corpo_taxa = f"""{TAXA_INICIO}
# GERADO por tools/exportar_prior.py, NAO EDITAR A MAO.
# cardId -> taxa suavizada de escolha quando oferecida, nos episodios de TREINO.
# {len(tabela)} cartas, suavizacao aditiva de {SUAVIZACAO:.0f} ofertas na media
# global ({media:.4f}). Cartas nunca vistas recebem TAXA_PADRAO.
TAXA_CARTA: dict[int, float] = {{
{textwrap.fill(itens, width=74, initial_indent="    ", subsequent_indent="    ")}
}}
TAXA_PADRAO = {media:.6g}
{TAXA_FIM}"""

    alvo = RAIZ / "submission" / "main.py"
    fonte = alvo.read_text(encoding="utf-8")
    a, b = fonte.index(INICIO), fonte.index(FIM) + len(FIM)
    fonte = fonte[:a] + corpo + fonte[b:]
    a, b = fonte.index(TAXA_INICIO), fonte.index(TAXA_FIM) + len(TAXA_FIM)
    fonte = fonte[:a] + corpo_taxa + fonte[b:]
    alvo.write_text(fonte, encoding="utf-8")
    print(f"injetado em {alvo.relative_to(RAIZ)} "
          f"({alvo.stat().st_size/1024:.0f} KB)")

    maiores = np.argsort(np.abs(lr.coef_[0]))[::-1][:10]
    print("\n  coeficientes de maior peso:")
    for i in maiores:
        print(f"    {agente.NOMES_FEATURES[i]:22} {lr.coef_[0][i]:+.3f}")


if __name__ == "__main__":
    main()
