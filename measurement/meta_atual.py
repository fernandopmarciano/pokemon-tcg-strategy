"""O campo de HOJE: participacao por arquetipo, com IC, e a lista representativa.

## Por que existe

O mapa de ameacas do projeto (`tools/avaliar_deck_vs_meta.py`) le
`data/analise/meta_prior.json`, que e de 11/08 e diz **Marnie's Grimmsnarl ex,
34,0%**. Medido em 28/08, o Grimmsnarl saiu do top 6 e o nosso proprio arquetipo
caiu a **zero em 1.600 lados** [0,00; 0,24]. A justificativa do deck estava
apoiada num campo que nao existe mais.

Esta ferramenta reconstroi aquele arquivo a partir dos episodios, para o
intervalo de dias que se pedir.

## O que ela mede, e com que unidade

A unidade e o **lado** (uma partida da dois lados). Para cada arquetipo:

  participacao   lados dele / lados totais, com IC de Wilson — nunca numero solto
  lista          a lista de 60 cartas MAIS FREQUENTE do arquetipo, com quantos
                 pilotos a jogam. Nao e "a melhor": e a modal, e o texto diz isso

## O que ela NAO faz

Nao decide nada e nao pilota ninguem. Participacao e conta de lado; o mapa de
ameacas que consome este arquivo e conta de carta. Quem mede forca e a bancada,
e a bancada tem um adversario forte so — ver `docs/por-que-lucario-2026-08-23.md`.

Uso:
    python tools/meta_atual.py --de 2026-08-23 --ate 2026-08-27
"""
from __future__ import annotations

import argparse
import collections
import json
import multiprocessing as mp
import pathlib
import sys

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import estatistica as est  # noqa: E402
from tendencia_ladder import arquetipo, carregar_cartas  # noqa: E402

_CARTAS: dict = {}


def _iniciar():
    global _CARTAS
    _CARTAS = carregar_cartas()


def lados(caminho: pathlib.Path) -> list[tuple[str, str]]:
    """(arquetipo, deck como string) por lado deste episodio."""
    try:
        ep = json.load(open(caminho, encoding="utf-8"))
    except Exception:
        return []
    vistos: dict[int, tuple[str, str]] = {}
    for passo in ep.get("steps", [])[:3]:
        for i, ag in enumerate(passo):
            a = ag.get("action")
            if not (isinstance(a, list) and len(a) == 60) or i in vistos:
                continue
            lista = [int(x) for x in a]
            vistos[i] = (arquetipo(lista, _CARTAS), " ".join(map(str, lista)))
    return list(vistos.values())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--de", default="2026-08-23")
    ap.add_argument("--ate", default="2026-08-27")
    ap.add_argument("--processos", type=int, default=max(1, mp.cpu_count() - 2))
    ap.add_argument("--min-lados", type=int, default=10,
                    help="arquetipos abaixo disso saem do arquivo")
    ap.add_argument("--saida", default="data/analise/meta_atual.json")
    # Conta lados que RODAM uma carta, independente do rotulo do arquetipo.
    #
    # Existe porque o rotulo engana: em 28/08 o arquetipo "Teal Mask Ogerpon ex"
    # media 0,1% do campo e parecia extinto — mas as listas de Hydrapple ex
    # (17,9%) rodam QUATRO copias da carta 96. Quem mediu o rotulo concluiu
    # "sumiu"; quem mede a carta ve o contrario. Medir o rotulo quando a
    # pergunta e sobre a CARTA foi a regua quebrada nº 11 do projeto.
    ap.add_argument("--carta", type=int, default=None,
                    help="id de carta: reporta em quantos lados ela aparece")
    args = ap.parse_args()

    arquivos = [p for p in sorted((RAIZ / "data" / "episodes").glob("*/*.json"))
                if args.de <= p.parent.name <= args.ate]
    print(f"  {len(arquivos)} episodios de {args.de} a {args.ate}"
          f" | {args.processos} processos")

    total = 0
    com_carta: collections.Counter = collections.Counter()
    copias: collections.Counter = collections.Counter()
    por_arq: collections.Counter = collections.Counter()
    listas: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter)
    feitos = 0
    with mp.Pool(args.processos, initializer=_iniciar) as pool:
        for parte in pool.imap_unordered(lados, arquivos, chunksize=4):
            for arq, deck in parte:
                total += 1
                por_arq[arq] += 1
                listas[arq][deck] += 1
                if args.carta is not None:
                    k = deck.split().count(str(args.carta))
                    if k:
                        com_carta[arq] += 1
                        copias[arq] += k
            feitos += 1
            if feitos % 250 == 0:
                print(f"  ... {feitos}/{len(arquivos)}, {total} lados",
                      flush=True)

    if not total:
        print("  NADA COLETADO.")
        return

    print(f"\n  {total} lados no periodo\n")
    print(f"  {'arquetipo':30s}{'lados':>7}{'uso':>8}{'IC 95%':>18}"
          f"{'lista modal':>14}")
    print("  " + "-" * 77)

    saida = []
    for arq, n in por_arq.most_common():
        p, lo, hi = est.wilson(n, total)
        modal, freq = listas[arq].most_common(1)[0]
        print(f"  {arq[:30]:30s}{n:7d}{p:8.1%}   [{lo:5.1%}; {hi:5.1%}]"
              f"{freq:>8d}/{n}")
        if n >= args.min_lados:
            saida.append({
                "arquetipo": arq,
                "uso": round(p * 100, 1),
                "uso_ic95": [round(lo * 100, 1), round(hi * 100, 1)],
                "lados": n,
                "lados_totais": total,
                "pilotos_da_lista_modal": freq,
                "deck": [int(x) for x in modal.split()],
            })

    if args.carta is not None:
        n_com = sum(com_carta.values())
        p, lo, hi = est.wilson(n_com, total)
        print("")
        print(f"  A CARTA {args.carta}, e nao o rotulo")
        print(f"  {'arquetipo':30s}{'lados com ela':>15}{'de':>7}{'copias/lado':>13}")
        print("  " + "-" * 66)
        for arq, n in com_carta.most_common():
            print(f"  {arq[:30]:30s}{n:>15}{por_arq[arq]:>7}"
                  f"{copias[arq]/n:>13.1f}")
        print("")
        print(f"  TOTAL: {n_com} de {total} lados = {p:.1%} [{lo:.1%}; {hi:.1%}]")

    destino = RAIZ / args.saida
    destino.parent.mkdir(parents=True, exist_ok=True)
    json.dump(saida, open(destino, "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(f"\n  {len(saida)} arquetipos (>= {args.min_lados} lados) em {destino}")
    print(f"  periodo {args.de} a {args.ate}, {total} lados")


if __name__ == "__main__":
    main()
