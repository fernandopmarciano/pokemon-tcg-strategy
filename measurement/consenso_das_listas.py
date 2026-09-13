"""O que as listas FORTES concordam, e onde a nossa diverge do consenso.

A pergunta do Fernando: avaliar os decks de Ogerpon com 1.000+ na ladder, e em
que eles superam o nosso.

A comparacao um-contra-um (a nossa contra a de maior rating) ja foi feita em
`distancia_das_listas.py` e mostrou 47 de 60 cartas em comum. Mas comparar com
UMA lista confunde escolha deliberada com idiossincrasia daquele piloto.

O que esta ferramenta faz e diferente: mede o CONSENSO. Uma carta que aparece
nas 14 listas fortes, na mesma quantidade, e escolha do arquetipo. Uma que
aparece em 1 e gosto pessoal. E o desvio da nossa lista em relacao ao consenso
e onde estamos apostando contra o campo — de proposito ou por descuido.

Tambem reporta os JOGOS: taxa de vitoria e ganho de Elo por equipe, para
separar "a lista e boa" de "o piloto e bom".

Uso:
    python tools/consenso_das_listas.py
    python tools/consenso_das_listas.py --corte 1100
"""
from __future__ import annotations

import argparse
import collections
import csv
import pathlib
import statistics
import sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "tools"))
import estatistica as est  # noqa: E402
from deck_em_uso import deck_em_uso  # noqa: E402

FONTE = RAIZ / "data" / "meta" / "tendencia_ladder.csv"
CARTAS = RAIZ / "data" / "EN_Card_Data.csv"
COL_TIPO = "Stage (Pokémon)/Type (Energy and Trainer)"


def catalogo() -> dict[str, tuple[str, str]]:
    info = {}
    with open(CARTAS, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            info.setdefault(r["Card ID"],
                            (r["Card Name"], (r.get(COL_TIPO) or "").strip()))
    return info


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arquetipo", default="Teal Mask Ogerpon ex")
    ap.add_argument("--corte", type=float, default=1000.0)
    # A regua quebrada nº 5: cravar a lista aqui a deixa velha em silencio.
    # Esta ferramenta ficou de fora da correcao de 18/08 e seguiu comparando
    # o campo com o **v6** ate 21/08, com o v8 embarcado ha dias.
    ap.add_argument("--nosso-deck", default=None)
    args = ap.parse_args()
    if args.nosso_deck is None:
        args.nosso_deck = deck_em_uso()

    info = catalogo()
    nome = lambda c: info.get(c, ("???", ""))[0]      # noqa: E731

    linhas = []
    with open(FONTE, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["arquetipo"] != args.arquetipo:
                continue
            try:
                r["rating"] = float(r["rating"])
                r["delta"] = float(r["delta"])
                r["vitoria"] = int(r["vitoria"])
            except (TypeError, ValueError):
                continue
            linhas.append(r)

    # uma lista por equipe (a do maior rating), so as fortes
    melhor: dict[str, dict] = {}
    for r in linhas:
        eq = r["equipe"]
        if eq not in melhor or r["rating"] > melhor[eq]["rating"]:
            melhor[eq] = r
    fortes = {eq: r for eq, r in melhor.items() if r["rating"] >= args.corte}

    nosso = collections.Counter(
        x.strip() for x in (RAIZ / args.nosso_deck).read_text(
            encoding="utf-8").splitlines() if x.strip())

    listas = {eq: collections.Counter(r["deck"].split())
              for eq, r in fortes.items()}
    n = len(listas)

    print(f"arquetipo: {args.arquetipo} | corte: {args.corte:.0f}")
    print(f"{n} listas fortes | nossa: {args.nosso_deck}\n")

    # ---------------------------------------------------- o consenso
    presenca: collections.Counter = collections.Counter()
    copias = collections.defaultdict(list)
    for c in listas.values():
        for cid, q in c.items():
            presenca[cid] += 1
            copias[cid].append(q)
    for cid in presenca:
        faltam = n - len(copias[cid])
        copias[cid] += [0] * faltam

    todas = sorted(set(presenca) | set(nosso),
                   key=lambda c: (-presenca[c], nome(c)))

    print("=" * 94)
    print("CONSENSO DAS LISTAS FORTES, E ONDE A NOSSA DIVERGE")
    print("=" * 94)
    print(f"\n  {'carta':<30} {'em':>5} {'mediana':>8} {'faixa':>9} "
          f"{'NOSSA':>7}  divergência")
    print("  " + "-" * 92)

    divergencias = []
    for cid in todas:
        emq = presenca[cid]
        med = statistics.median(copias[cid]) if copias[cid] else 0
        faixa = (f"{min(copias[cid])}-{max(copias[cid])}"
                 if copias[cid] else "—")
        meu = nosso[cid]
        d = meu - med
        if emq == 0:
            marca = "SÓ NOSSA"
        elif meu == 0 and emq == n:
            marca = "UNÂNIME e não temos"
        elif meu == 0:
            marca = "não temos"
        elif abs(d) >= 2:
            marca = f"{d:+.0f} vs consenso"
        elif emq == n and meu == med:
            marca = "de acordo"
        else:
            marca = ""
        if marca and marca != "de acordo":
            divergencias.append((abs(d), cid, emq, med, meu, marca))
        print(f"  {nome(cid)[:30]:<30} {emq:>3}/{n} {med:>8.0f} {faixa:>9} "
              f"{meu:>7}  {marca}")

    # ------------------------------------------------- o que mais divergimos
    print("\n" + "=" * 94)
    print("AS APOSTAS: onde a nossa lista mais se afasta do consenso")
    print("=" * 94 + "\n")
    for _, cid, emq, med, meu, marca in sorted(divergencias, reverse=True)[:12]:
        print(f"  {nome(cid)[:32]:<32} consenso {med:.0f} "
              f"(em {emq}/{n})   nossa {meu}   -> {marca}")

    # ------------------------------------------------------------- os jogos
    print("\n" + "=" * 94)
    print("OS JOGOS DESSAS EQUIPES")
    print("=" * 94)
    print(f"\n  {'equipe':<26} {'rating':>7} {'part.':>6} {'vitórias':>20} "
          f"{'Elo/partida':>12}")
    print("  " + "-" * 92)

    tot_v = tot_n = 0
    todos_deltas = []
    for eq, r in sorted(fortes.items(), key=lambda kv: -kv[1]["rating"]):
        ms = [x for x in linhas if x["equipe"] == eq]
        v = sum(x["vitoria"] for x in ms)
        tot_v += v
        tot_n += len(ms)
        ds = [x["delta"] for x in ms]
        todos_deltas += ds
        p, lo, hi = est.wilson(v, len(ms))
        print(f"  {eq[:26]:<26} {r['rating']:>7.0f} {len(ms):>6} "
              f"{est.formatar(p, lo, hi):>20} {statistics.mean(ds):>+11.2f}")

    p, lo, hi = est.wilson(tot_v, tot_n)
    print(f"\n  {'AGREGADO':<26} {'':>7} {tot_n:>6} {est.formatar(p, lo, hi):>20} "
          f"{statistics.mean(todos_deltas):>+11.2f}")

    if len(todos_deltas) > 1:
        s = statistics.stdev(todos_deltas)
        t = est._t_critico(len(todos_deltas) - 1)
        m = statistics.mean(todos_deltas)
        meia = t * s / (len(todos_deltas) ** 0.5)
        print(f"  IC 95% do Elo por partida: [{m-meia:+.2f}; {m+meia:+.2f}] "
              f"(t, {len(todos_deltas)-1} g.l.)")

    print(f"""
=============================================================================
COMO LER
=============================================================================

  "UNANIME e nao temos" e o achado mais forte que esta tabela pode dar: uma
  carta que as {n} listas fortes jogam e nos nao. Se existir, e a hipotese mais
  barata do projeto.

  "SO NOSSA" e o oposto — uma aposta que ninguem do campo faz. Pode ser
  vantagem competitiva ou pode ser erro; a tabela nao decide, so aponta.

  A taxa de vitoria dessas equipes NAO e comparavel com a nossa do painel: elas
  jogam contra o campo da ladder na altura delas, e nos contra quatro
  adversarios fixos. Serve para separar "a lista e boa" de "o piloto e bom" —
  se todas as {n} ganham, e a lista.
""")


if __name__ == "__main__":
    main()
