"""Analise completa de uma lista: composicao, energia, corrida de premios.

Junta num lugar so o que estava espalhado em cinco scripts: contagem por
categoria, matematica de energia (quantos anexos por turno o deck sustenta),
corrida de premios contra o meta ponderado, e o efeito de por atacantes de
1 PREMIO na lista.

Uso:
    python tools/analisar_deck.py --deck decks/ogerpon_v2.csv
    python tools/analisar_deck.py --deck decks/ogerpon_v2.csv --comparar decks/ogerpon_v1.csv
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "engine"))
sys.path.insert(0, str(RAIZ / "submission"))
sys.path.insert(0, str(RAIZ / "tools"))
from deck_em_uso import deck_em_uso  # noqa: E402

from cg.api import CardType, EnergyType, all_attack, all_card_data  # noqa: E402

C = {c.cardId: c for c in all_card_data()}
A = {a.attackId: a for a in all_attack()}
PREMIOS_TOTAIS = 6


def ler(p):
    caminho = pathlib.Path(p)
    if not caminho.is_absolute():
        caminho = RAIZ / p
    return [int(x) for x in caminho.read_text(encoding="utf-8")
            .replace(",", "\n").split() if x.strip()]


def premios(c) -> int:
    return 3 if c.megaEx else 2 if c.ex else 1


def composicao(deck):
    cont = collections.Counter(deck)
    por_tipo = collections.Counter()
    for cid, n in cont.items():
        por_tipo[CardType(int(C[cid].cardType)).name] += n
    return cont, por_tipo


def secao(titulo):
    print(f"\n{'=' * 78}\n{titulo}\n{'=' * 78}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default=deck_em_uso())
    ap.add_argument("--comparar", default=None)
    args = ap.parse_args()

    deck = ler(args.deck)
    cont, por_tipo = composicao(deck)
    nome = pathlib.Path(args.deck).name

    secao(f"COMPOSICAO — {nome} ({len(deck)} cartas)")
    ordem = ["POKEMON", "ITEM", "TOOL", "SUPPORTER", "STADIUM",
             "BASIC_ENERGY", "SPECIAL_ENERGY"]
    for t in ordem:
        n = por_tipo.get(t, 0)
        if not n:
            continue
        print(f"\n  {t}  —  {n} cartas ({100*n/len(deck):.0f}% do deck)")
        for cid, q in sorted(cont.items(), key=lambda kv: -kv[1]):
            if CardType(int(C[cid].cardType)).name != t:
                continue
            extra = ""
            if t == "POKEMON":
                c = C[cid]
                extra = (f"  [{EnergyType(c.energyType).name}, {c.hp} PS, "
                         f"{premios(c)} premio(s), recuo {c.retreatCost}"
                         + (", Tera" if c.tera else "") + "]")
            print(f"     {q}x {C[cid].name}{extra}")

    if args.comparar:
        outro = ler(args.comparar)
        c2, _ = composicao(outro)
        secao(f"DIFERENCA CONTRA {pathlib.Path(args.comparar).name}")
        for cid in sorted(set(cont) | set(c2), key=lambda i: C[i].name):
            a, b = c2.get(cid, 0), cont.get(cid, 0)
            if a != b:
                print(f"  {C[cid].name:<28} {a} -> {b}   "
                      f"({'+' if b > a else ''}{b - a})")

    # --------------------------------------------------- energia
    secao("MATEMATICA DE ENERGIA")
    basica_g = sum(n for cid, n in cont.items()
                   if int(C[cid].cardType) == 5 and int(C[cid].energyType) == 1)
    especial = sum(n for cid, n in cont.items() if int(C[cid].cardType) == 6)
    total_e = basica_g + especial
    print(f"  Energia {{G}} basica : {basica_g}")
    print(f"  Energia especial   : {especial}")
    print(f"  TOTAL              : {total_e}  ({100*total_e/len(deck):.0f}% do deck)")
    print("\n  Anexos por turno que o deck sustenta:")
    print("    1 manual  (aceita QUALQUER energia, inclusive a especial)")
    print("    1 por Ogerpon ex em jogo, via Teal Dance "
          "(so aceita {G} BASICA, e anexa a SI MESMO)")
    print("  -> com 2 Ogerpon ex em campo, ate 3 anexos por turno")
    print("\n  O manual e o Teal Dance NAO competem: a especial so entra pelo")
    print("  manual, e o Teal Dance so aceita basica. Cada um tem a sua fonte.")

    # --------------------------------------------------- corrida de premios
    secao("CORRIDA DE PREMIOS")
    pk = [(cid, n) for cid, n in cont.items() if int(C[cid].cardType) == 0]
    print(f"  {'Pokemon':<28} {'copias':>7} {'PS':>5} {'premios':>8}")
    for cid, n in sorted(pk, key=lambda kv: -C[kv[0]].hp):
        c = C[cid]
        print(f"  {c.name:<28} {n:>7} {c.hp:>5} {premios(c):>8}")

    distintos = {premios(C[cid]) for cid, _ in pk}
    if distintos == {2}:
        print("\n  Todos valem 2 premios -> o adversario fecha em 3 NOCAUTES.")
    else:
        print(f"\n  Valores distintos em jogo: {sorted(distintos)}")

    print(f"\n  Se ele nocautear so Pokemon de 2 premios : "
          f"{-(-PREMIOS_TOTAIS // 2)} nocautes")
    print(f"  Com UM de 1 premio no meio               : "
          f"1 + {-(-(PREMIOS_TOTAIS - 1) // 2)} = "
          f"{1 + -(-(PREMIOS_TOTAIS - 1) // 2)} nocautes")
    print(f"  Com DOIS de 1 premio                     : "
          f"2 + {-(-(PREMIOS_TOTAIS - 2) // 2)} = "
          f"{2 + -(-(PREMIOS_TOTAIS - 2) // 2)} nocautes")

    # --------------------------------------------------- 1 premio disponiveis
    secao("ATACANTES DE 1 PREMIO DISPONIVEIS (grama, basicos)")
    print("  Trocar um nocaute de 2 premios por um de 1 obriga o adversario a")
    print("  um nocaute A MAIS. O preco e um atacante pior na frente.\n")
    print(f"  {'carta':<26} {'PS':>5} {'recuo':>6} {'Tera':>5}  ataques")
    for c in sorted(C.values(), key=lambda x: -x.hp):
        if int(c.cardType) != 0 or not c.basic or c.ex or c.megaEx:
            continue
        if int(c.energyType) != 1 or not (c.attacks or []):
            continue
        if "Ogerpon" not in c.name and c.hp < 100:
            continue
        linhas = []
        for aid in c.attacks:
            a = A.get(aid)
            if a:
                linhas.append(f"{a.name} (custo {len(a.energies)}, dano {a.damage})")
        print(f"  {c.name:<26} {c.hp:>5} {c.retreatCost:>6} "
              f"{'sim' if c.tera else 'nao':>5}  {' | '.join(linhas)}")


if __name__ == "__main__":
    main()
