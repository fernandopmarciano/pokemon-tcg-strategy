"""Arena multiprocesso — o L1c contra a regua nova, com N que separa hipoteses.

Por que multiprocesso e nao threads: o `cg.dll` guarda o estado da partida em
variaveis globais do modulo. `battle_start` / `battle_select` / `battle_finish`
operam sobre UMA partida por processo. Threads compartilhariam esse estado e
embaralhariam as partidas em silencio — o pior tipo de bug, porque o resultado
sai plausivel.

Por que budget reduzido no ref950: o original gasta 1,5 s por decisao MAIN, o
que da ~2 minutos de agente por partida. Com N na casa dos milhares seria
inviavel localmente. O budget usado sai no relatorio; comparacao com budget
diferente nao e a mesma comparacao.

O engine e ESTOCASTICO e nao aceita seed, entao nao existe partida pareada:
toda comparacao e entre amostras independentes, com IC de Wilson e replicas.

Uso:
    python tools/arena_paralela.py --a l1c --b ref950 --n 2000 --replicas 5
    python tools/arena_paralela.py --a l1c --b ref950 --deck-a decks/ogerpon_v1.csv
"""
from __future__ import annotations

import argparse
import math
import multiprocessing as mp
import pathlib
import statistics
import time

RAIZ = pathlib.Path(__file__).resolve().parents[1]
MAX_DECISOES = 2000


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    if n == 0:
        return (float("nan"),) * 3
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centro - meia), min(1.0, centro + meia)


def ler_deck(caminho: str | pathlib.Path) -> list[int]:
    txt = pathlib.Path(caminho).read_text(encoding="utf-8")
    deck = [int(x) for x in txt.replace(",", "\n").split() if x.strip()]
    if len(deck) != 60:
        raise ValueError(f"{caminho}: {len(deck)} cartas")
    return deck


# ------------------------------------------------------------- agentes
# Cada worker monta os agentes uma vez; sao closures sobre o modulo do engine
# ja importado no processo.
def montar_agentes(nomes: tuple[str, str], budget: float, deck_ref: list[int],
                   deck_nosso: list[int] | None = None):
    """Monta os dois agentes. `deck_nosso` e a lista que NOS estamos jogando.

    BUG CORRIGIDO em 2026-08-11, e ele contaminava toda comparacao de deck.
    Antes, o agente determinizava com `h.MY_DECK`, que le `submission/deck.csv`
    — um arquivo parado desde o primeiro commit, com um deck de METAL (Mega
    Mawile ex, Zacian ex, 14 Energias de Metal). Jogando o deck de agua do
    sample, a busca preenchia o nosso deck e os nossos premios com cartas que
    nao existiam na partida.

    O preco, medido: o Hammer-lanche do Mega Abomasnow ex descarta o topo 6 e
    bate 100 por Energia de Agua descartada. Dentro da busca, com o deck de
    metal, ele deu ZERO em 100% das 136 simulacoes; com o deck certo, media
    130 e maximo 350. O agente simulava o proprio nuke como um ataque inerte.

    SEGUNDO DEFEITO, LATENTE ATE 23/08 — a mesma regua quebrada nº 5, esperando
    a primeira partida de ESPELHO. O laco era `for nome in set(nomes)` e o
    resultado, um dicionario por NOME. Com `--a l1c --b l1c`, `set` colapsa os
    dois lados num agente so, que determiniza com `deck_nosso` — o deck do lado
    A. **O adversario simularia o futuro com o NOSSO baralho.**

    Nunca disparou porque ninguem tinha rodado l1c contra l1c. E e exatamente a
    configuracao necessaria para as casas de META funcionarem: o `ref950` tem
    identificadores cravados e nao pilota outra lista (ganhamos 93 a 99% delas),
    enquanto o `l1c` e agnostico de baralho.

    A correcao devolve **um agente por LADO**, cada um com o seu deck, e por
    isso a funcao passou a devolver uma TUPLA (agente_a, agente_b) em vez de um
    dicionario por nome.
    """
    import sys
    sys.path.insert(0, str(RAIZ / "engine"))
    sys.path.insert(0, str(RAIZ / "submission"))
    sys.path.insert(0, str(RAIZ))

    def primeira(obs):
        sel = obs.get("select") or {}
        return list(range(max(1, sel.get("minCount") or 1)))

    def montar_um(nome: str, deck_do_lado: list[int]):
        """Um agente, com o deck QUE ELE ESTA JOGANDO — nunca o do outro lado."""
        if nome == "primeira":
            return primeira
        if nome in ("l0", "l1c"):
            import main as h
            usa_busca = nome == "l1c"

            # o deck da determinizacao e o que ESTE LADO esta jogando, nunca o
            # MY_DECK e nunca o deck do adversario
            meu = list(deck_do_lado or h.MY_DECK)

            def agente(obs, h=h, usa_busca=usa_busca, meu=meu):
                sel = obs.get("select") or {}
                opts = sel.get("option") or []
                notas = None
                if usa_busca:
                    notas = h.escolher_por_busca(obs, meu, time.time() + 3.0)
                if notas is None:
                    notas = h.score_options(opts)
                return h.select_indices(notas, sel.get("minCount") or 1,
                                        sel.get("maxCount") or 1)
            return agente
        if nome == "ref950":
            from tools.oponentes import ref950
            ref950.definir_budget(budget)
            ref950.definir_deck(deck_do_lado)
            return ref950.agent
        raise ValueError(f"agente desconhecido: {nome}")

    # A ordem importa: o lado A joga `deck_nosso` e o lado B joga `deck_ref`.
    return (montar_um(nomes[0], deck_nosso), montar_um(nomes[1], deck_ref))


def lote(args) -> tuple[int, int, int, float]:
    """Joga `n` partidas num processo. Devolve (vitorias de A, validas, decisoes, s)."""
    nome_a, nome_b, deck_a, deck_b, n, semente, budget = args

    import sys
    sys.path.insert(0, str(RAIZ / "engine"))
    from cg.game import battle_finish, battle_select, battle_start

    fa, fb = montar_agentes((nome_a, nome_b), budget, deck_b, deck_a)

    vitorias = validas = decisoes = 0
    t0 = time.perf_counter()
    for i in range(n):
        # alterna quem comeca: a posicao importa e nao ha partida pareada
        a_comeca = (semente + i) % 2 == 0
        d0, d1 = (deck_a, deck_b) if a_comeca else (deck_b, deck_a)
        g0, g1 = (fa, fb) if a_comeca else (fb, fa)
        obs, sd = battle_start(d0, d1)
        if obs is None:
            continue
        try:
            venc = None
            for _ in range(MAX_DECISOES):
                atual = obs.get("current") or {}
                r = atual.get("result", -1)
                if r != -1:
                    venc = r
                    break
                sel = obs.get("select")
                if not sel or not sel.get("option"):
                    venc = r
                    break
                g = g0 if atual.get("yourIndex") == 0 else g1
                try:
                    escolha = g(obs)
                except Exception:
                    escolha = list(range(max(1, sel.get("minCount") or 1)))
                obs = battle_select(escolha)
                decisoes += 1
        finally:
            battle_finish()
        if venc is None or venc < 0:
            continue
        validas += 1
        vitorias += int(venc == (0 if a_comeca else 1))
    return vitorias, validas, decisoes, time.perf_counter() - t0


def rodar(nome_a, nome_b, deck_a, deck_b, n, jobs, budget, semente=0):
    por_job = [n // jobs + (1 if i < n % jobs else 0) for i in range(jobs)]
    tarefas = [(nome_a, nome_b, deck_a, deck_b, k, semente + i * 7919, budget)
               for i, k in enumerate(por_job) if k]
    with mp.Pool(len(tarefas)) as pool:
        res = pool.map(lote, tarefas)
    v = sum(r[0] for r in res)
    val = sum(r[1] for r in res)
    dec = sum(r[2] for r in res)
    return v, val, dec


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="l1c")
    ap.add_argument("--b", default="ref950")
    ap.add_argument("--n", type=int, default=400, help="partidas por replica")
    ap.add_argument("--replicas", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=max(1, (mp.cpu_count() or 4) - 1))
    ap.add_argument("--budget", type=float, default=0.05,
                    help="segundos por decisao MAIN do ref950")
    ap.add_argument("--deck-a", default=None)
    ap.add_argument("--deck-b", default=None)
    args = ap.parse_args()

    padrao = RAIZ / "data" / "competition_2026-08-06" / "deck.csv"
    deck_a = ler_deck(args.deck_a or padrao)
    deck_b = ler_deck(args.deck_b or padrao)

    print(f"{args.a} vs {args.b} | {args.replicas} replicas de {args.n} "
          f"| {args.jobs} processos | budget do ref {args.budget}s")
    print(f"deck A: {args.deck_a or 'sample'}")
    print(f"deck B: {args.deck_b or 'sample'}\n")

    taxas = []
    tot_v = tot_n = 0
    t0 = time.time()
    for r in range(args.replicas):
        v, n, dec = rodar(args.a, args.b, deck_a, deck_b, args.n, args.jobs,
                          args.budget, semente=r * 104729)
        p, lo, hi = wilson(v, n)
        taxas.append(p)
        tot_v += v
        tot_n += n
        print(f"  replica {r+1}: {v}/{n} = {p*100:5.1f}%  "
              f"[{lo*100:.1f}; {hi*100:.1f}]  ({dec} decisoes)", flush=True)

    p, lo, hi = wilson(tot_v, tot_n)
    print(f"\n{'='*66}")
    print(f"AGREGADO  {tot_v}/{tot_n} = {p*100:.1f}%   IC 95% Wilson "
          f"[{lo*100:.1f}; {hi*100:.1f}]")
    if len(taxas) > 1:
        print(f"dispersao entre replicas: {statistics.stdev(taxas)*100:.1f}pp "
              f"(min {min(taxas)*100:.1f}%, max {max(taxas)*100:.1f}%)")
    if lo > 0.5:
        print(f"=> {args.a} e melhor: o IC inteiro esta acima de 50%")
    elif hi < 0.5:
        print(f"=> {args.b} e melhor: o IC inteiro esta abaixo de 50%")
    else:
        print("=> indistinguivel de 50% com este N")
    print(f"tempo: {time.time()-t0:.0f}s")


if __name__ == "__main__":
    mp.freeze_support()
    main()
