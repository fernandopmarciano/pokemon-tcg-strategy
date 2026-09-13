"""O agente usa cada carta quando ela e oferecida?

Uma carta pode ser otima e nunca ser jogada. Antes de mexer em quantidade de
copias, vale saber a taxa de uso de cada uma: aumentar copias de uma carta que
o agente ignora e piorar o deck, e reduzir copias de uma que ele usa sempre e
tirar dele o que funciona.

Conta, por carta: quantas vezes ela apareceu como opcao numa decisao nossa e em
quantas o agente a escolheu.

Uso:
    python tools/medir_uso_cartas.py --n 60
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

from cg.api import all_card_data  # noqa: E402
from cg.game import battle_finish, battle_select, battle_start  # noqa: E402

C = {c.cardId: c for c in all_card_data()}


def ler(p):
    caminho = pathlib.Path(p)
    if not caminho.is_absolute():
        caminho = RAIZ / p
    return [int(x) for x in caminho.read_text(encoding="utf-8")
            .replace(",", "\n").split() if x.strip()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--deck", default=deck_em_uso())
    ap.add_argument("--deck-b", default="decks/ref950_lucario.csv")
    args = ap.parse_args()

    import main as h

    meu = ler(args.deck)
    dele = ler(args.deck_b)
    no_deck = collections.Counter(meu)

    ofertado: collections.Counter = collections.Counter()
    usado: collections.Counter = collections.Counter()
    # POR TURNO — a unidade que importa. A metrica por decisao engana: uma
    # carta e oferecida em TODA decisao do turno ate ser jogada, entao contar
    # por decisao subestima o uso. Medido no Teal Dance: 40% por decisao
    # contra 90,6% por turno.
    of_turno: collections.Counter = collections.Counter()
    us_turno: collections.Counter = collections.Counter()
    # contexto no momento em que o Judge foi oferecido
    judge_mao_nossa, judge_mao_dele = [], []

    for partida in range(args.n):
        eu = partida % 2
        d0, d1 = (meu, dele) if eu == 0 else (dele, meu)
        obs, sd = battle_start(d0, d1)
        if obs is None:
            continue
        turno_atual = None
        of_no_turno: set = set()
        us_no_turno: set = set()
        try:
            for _ in range(400):
                atual = obs.get("current") or {}
                if atual.get("result", -1) != -1:
                    break
                sel = obs.get("select") or {}
                opts = sel.get("option") or []
                if not opts:
                    break
                t = int(atual.get("turn", 0) or 0)
                if atual.get("yourIndex") == eu and t != turno_atual:
                    for cid in of_no_turno:
                        of_turno[cid] += 1
                    for cid in us_no_turno:
                        us_turno[cid] += 1
                    turno_atual, of_no_turno, us_no_turno = t, set(), set()

                if atual.get("yourIndex") == eu:
                    escolha = h.agent(obs)
                    vistos = set()
                    for i, op in enumerate(opts):
                        cid = h._carta_da_opcao(op, atual, sel, eu)
                        if cid is None or cid not in no_deck:
                            continue
                        if cid not in vistos:
                            ofertado[cid] += 1
                            vistos.add(cid)
                            of_no_turno.add(cid)
                        if escolha and i in escolha:
                            usado[cid] += 1
                            us_no_turno.add(cid)
                    if 1213 in vistos:  # Judge
                        jog = (atual.get("players") or [])
                        judge_mao_nossa.append(
                            len((jog[eu] or {}).get("hand") or []))
                        judge_mao_dele.append(
                            (jog[1 - eu] or {}).get("handCount") or 0)
                else:
                    escolha = list(range(max(1, sel.get("minCount") or 1)))
                obs = battle_select(escolha)
        finally:
            battle_finish()

    print(f"deck: {pathlib.Path(args.deck).name} vs "
          f"{pathlib.Path(args.deck_b).name} | {args.n} partidas\n")
    print(f"  {'carta':<28} {'cop':>4} | {'POR TURNO':^22} | {'por decisao':^16}")
    print(f"  {'':<28} {'':>4} | {'ofert':>7}{'usou':>7}{'taxa':>8} | "
          f"{'ofert':>7}{'taxa':>8}")
    print("  " + "-" * 78)
    linhas = []
    for cid, n in no_deck.items():
        c = C.get(cid)
        if not c or int(c.cardType) in (0, 5, 6):
            continue  # Pokemon e energia entram por outro caminho
        linhas.append((of_turno.get(cid, 0), cid, n))
    for _, cid, n in sorted(linhas, reverse=True):
        oft, ust = of_turno.get(cid, 0), us_turno.get(cid, 0)
        ofd, usd = ofertado.get(cid, 0), usado.get(cid, 0)
        tt = f"{100*ust/oft:.0f}%" if oft else "—"
        td = f"{100*usd/ofd:.0f}%" if ofd else "—"
        print(f"  {C[cid].name:<28} {n:>4} | {oft:>7}{ust:>7}{tt:>8} | "
              f"{ofd:>7}{td:>8}")

    if judge_mao_nossa:
        import statistics
        print(f"\n  quando o Judge foi oferecido ({len(judge_mao_nossa)} vezes):")
        print(f"    cartas na NOSSA mao : media "
              f"{statistics.mean(judge_mao_nossa):.1f}  "
              f"(<=1 em {100*sum(1 for x in judge_mao_nossa if x <= 1)/len(judge_mao_nossa):.0f}%)")
        print(f"    cartas na mao DELE  : media "
              f"{statistics.mean(judge_mao_dele):.1f}  "
              f"(>=6 em {100*sum(1 for x in judge_mao_dele if x >= 6)/len(judge_mao_dele):.0f}%)")


if __name__ == "__main__":
    main()
