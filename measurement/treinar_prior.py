"""Treina o prior de politica: dado o estado e as opcoes, qual um jogador de
rating ~1.100 escolheria.

Nao e classificacao comum e sim learning-to-rank: o que importa nao e acertar a
probabilidade de cada opcao isolada, e sim **por a opcao certa em primeiro**,
porque o uso e ordenar o feixe da busca.

Split POR EPISODIO, nunca por linha. Decisoes da mesma partida sao
correlacionadas — dividir por linha vazaria o mesmo jogo para treino e teste e
inflaria a metrica.

Metrica: top-1 por decisao, contra a linha de base de escolher ao acaso
(1 / numero de opcoes) e contra a heuristica L0 que o agente ja usa.

Uso:
    python tools/treinar_prior.py
"""
from __future__ import annotations

import argparse
import collections
import csv
import glob
import pathlib
import sys

import numpy as np

RAIZ = pathlib.Path(__file__).resolve().parents[1]

NUMERICAS = ["turno", "meus_premios", "premios_dele", "meu_hp", "hp_dele",
             "minha_energia", "energia_dele", "meu_banco", "banco_dele",
             "minha_mao", "mao_dele", "meu_deck", "apoiador_jogado",
             "energia_anexada", "recuou", "n_opcoes", "indice",
             # da opcao: quem ela mexe e o que ela faz. Antes eram colunas
             # mortas — `carta_tipo` vinha vazia em 100% das linhas porque so
             # o tipo SKILL carrega cardId. Agora vem da resolucao
             # area+index+playerIndex, que cobre 52%.
             "carta_ex", "carta_hp", "dano", "letal"]
TIPOS = list(range(17))
CLASSES_CARTA = ["Basic Pokémon", "Stage 1 Pokémon", "Stage 2 Pokémon",
                 "Pokémon Tool", "Item", "Supporter", "Stadium",
                 "Special Energy", "Basic Energy", ""]


def carregar():
    linhas = []
    for f in sorted(glob.glob(str(RAIZ / "data" / "analise" / "imitacao_*.csv"))):
        with open(f, encoding="utf-8") as fh:
            linhas += list(csv.DictReader(fh))
    return linhas


def matriz(linhas):
    n = len(linhas)
    X = np.zeros((n, len(NUMERICAS) + len(TIPOS) + len(CLASSES_CARTA)),
                 dtype=np.float32)
    y = np.zeros(n, dtype=np.int8)
    grupo = np.empty(n, dtype=object)
    for i, l in enumerate(linhas):
        for j, c in enumerate(NUMERICAS):
            try:
                X[i, j] = float(l[c])
            except (ValueError, KeyError):
                pass
        t = int(l["tipo"])
        if 0 <= t < len(TIPOS):
            X[i, len(NUMERICAS) + t] = 1.0
        ct = l.get("carta_tipo", "")
        if ct in CLASSES_CARTA:
            X[i, len(NUMERICAS) + len(TIPOS) + CLASSES_CARTA.index(ct)] = 1.0
        y[i] = int(l["escolhida"])
        grupo[i] = (l["episodio"], l["passo"])
    return X, y, grupo


def top1(scores, grupo, y):
    """Fracao das decisoes em que a opcao escolhida ficou em primeiro."""
    por: dict = collections.defaultdict(list)
    for i, g in enumerate(grupo):
        por[g].append(i)
    acertos = 0
    for g, idxs in por.items():
        melhor = max(idxs, key=lambda i: scores[i])
        acertos += int(y[melhor] == 1)
    return acertos / max(len(por), 1), len(por)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teste", type=float, default=0.25)
    args = ap.parse_args()

    linhas = carregar()
    if not linhas:
        raise SystemExit("sem dados — rode tools/coletar_imitacao.py")

    # SPLIT POR EPISODIO: decisoes da mesma partida sao correlacionadas
    episodios = sorted({l["episodio"] for l in linhas})
    rng = np.random.default_rng(20260810)
    rng.shuffle(episodios)
    corte = int(len(episodios) * (1 - args.teste))
    treino_eps = set(episodios[:corte])

    tr = [l for l in linhas if l["episodio"] in treino_eps]
    te = [l for l in linhas if l["episodio"] not in treino_eps]
    print(f"{len(linhas)} linhas | {len(episodios)} episodios")
    print(f"  treino: {len(tr)} linhas, {len(treino_eps)} episodios")
    print(f"  teste : {len(te)} linhas, {len(episodios)-len(treino_eps)} episodios")
    print("  (split por EPISODIO — por linha vazaria a mesma partida)\n")

    Xtr, ytr, gtr = matriz(tr)
    Xte, yte, gte = matriz(te)

    # base 1: acaso
    por = collections.Counter(gte)
    acaso = sum(1 / n for n in por.values()) / len(por)

    # base 2: a heuristica L0 que o agente ja usa
    sys.path.insert(0, str(RAIZ / "submission"))
    sys.path.insert(0, str(RAIZ / "engine"))
    import main as h
    l0 = np.array([h.BASE_PRIORITY.get(int(l["tipo"]), h.OTHER_PRIORITY)
                   - 0.001 * int(l["indice"]) for l in te], dtype=np.float32)
    p_l0, n_dec = top1(l0, gte, yte)

    print(f"{'modelo':28}{'top-1':>9}{'ganho s/ acaso':>17}")
    print("-" * 54)
    print(f"{'acaso':28}{100*acaso:8.1f}%{'—':>17}")
    print(f"{'heuristica L0 (atual)':28}{100*p_l0:8.1f}%{100*(p_l0-acaso):+16.1f}pp")

    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    esc = StandardScaler().fit(Xtr)
    lr = LogisticRegression(max_iter=1000, C=1.0)
    lr.fit(esc.transform(Xtr), ytr)
    s = lr.decision_function(esc.transform(Xte))
    p_lr, _ = top1(s, gte, yte)
    print(f"{'regressao logistica':28}{100*p_lr:8.1f}%{100*(p_lr-acaso):+16.1f}pp")

    import lightgbm as lgb
    gbm = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05,
                             num_leaves=63, verbose=-1)
    gbm.fit(Xtr, ytr)
    s = gbm.predict_proba(Xte)[:, 1]
    p_gbm, _ = top1(s, gte, yte)
    print(f"{'gradient boosting':28}{100*p_gbm:8.1f}%{100*(p_gbm-acaso):+16.1f}pp")

    print(f"\n  {n_dec} decisoes no teste")
    print("\n  features mais importantes (gradient boosting):")
    nomes = NUMERICAS + [f"tipo={t}" for t in TIPOS] + \
        [f"carta={c or 'nenhuma'}" for c in CLASSES_CARTA]
    ordem = np.argsort(gbm.feature_importances_)[::-1][:12]
    for i in ordem:
        print(f"    {nomes[i]:24} {gbm.feature_importances_[i]:.0f}")


if __name__ == "__main__":
    main()
