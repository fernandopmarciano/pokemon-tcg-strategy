"""Compara dois decks com REPLICAS, alternando — o protocolo que a regra pede.

Por que replicas: o engine e estocastico e NAO aceita semente. Medido em 13/08,
o MESMO deck v2 rodou 7 vezes na mesma sessao e variou de 47,8% a 50,2% —
desvio padrao de 0,96 pp entre rodadas, 1,1x o que o IC binomial preveria. Uma
medicao de cada lado nao separa +2,4 pp de ruido.

Por que ALTERNANDO (A, B, A, B, ...) e nao em bloco: se a maquina esquentar,
outro processo subir, ou qualquer deriva acontecer no meio, ela se distribui
igualmente entre os dois em vez de virar diferenca sistematica.

Reporta media +- desvio amostral (ddof=1) e o IC 95% da diferenca.

Uso:
    python tools/comparar_decks.py --a decks/ogerpon_v6.csv --b decks/ogerpon_v2.csv --replicas 5
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import os
import pathlib
import re
import statistics
import subprocess
import sys
import tempfile
import time

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
import estatistica as est  # noqa: E402

PY = sys.executable


def uma_rodada(deck: str, n: int,
               variante: str = "atual") -> tuple[float | None, dict[str, float]]:
    """Roda o painel uma vez e devolve (agregado, taxa por casa).

    O painel ja media as quatro casas a cada chamada; ate 18/08 esta funcao
    lia so o agregado da tela e jogava o resto fora. O gate do projeto e
    CONJUNTIVO — vencer no agregado E nao regredir em nenhuma casa — entao o
    dado descartado era exatamente metade do criterio. O T1 (Lively Stadium)
    gastou 198 min e 88.000 partidas e mesmo assim nao pode ser decidido,
    porque o recorte por casa nao existia mais.
    """
    fd, caminho = tempfile.mkstemp(suffix=".json", prefix="painel_")
    os.close(fd)
    try:
        cmd = [PY, "tools/painel.py", "--variantes", variante,
               "--n", str(n), "--replicas", "1", "--deck-a", deck,
               "--json", caminho]
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", cwd=str(RAIZ),
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        saida = r.stdout or ""
        por_casa: dict[str, float] = {}
        try:
            bruto = json.loads(pathlib.Path(caminho).read_text(encoding="utf-8"))
            por_casa = {casa: vit / n_casa
                        for casa, (vit, n_casa) in bruto[variante].items()
                        if n_casa}
        except (OSError, ValueError, KeyError):
            pass  # painel antigo ou rodada que falhou: segue so com o agregado
    finally:
        pathlib.Path(caminho).unlink(missing_ok=True)

    # a ultima porcentagem da linha da variante no bloco AGREGADO. Ela e a
    # unica da rodada, entao o painel a marca com `<- base`.
    m = re.search(rf"^\s*{re.escape(variante)}\s+.*?([\d.]+)%\s*<- base",
                  saida, re.M)
    if not m:
        m = re.findall(r"([\d.]+)%", saida)
        return (float(m[-1]) / 100 if m else None), por_casa
    return float(m.group(1)) / 100, por_casa


def _por_casa(casas_a: dict[str, list[float]], casas_b: dict[str, list[float]],
              na: str, nb: str, vencedor: str | None) -> None:
    """A outra metade do gate: nao regredir em NENHUMA casa.

    Ganhar no agregado nao basta. O criterio e conjuntivo desde que uma regua
    unica enganou a medicao tres vezes, e o agregado pode esconder uma casa em
    que a mudanca desaba — que e justamente o formato de "depender de matchup"
    que a rubrica pergunta.
    """
    comuns = [c for c in casas_a if c in casas_b
              and len(casas_a[c]) > 1 and len(casas_b[c]) > 1]
    if not comuns:
        print("\n  AVISO: sem recorte por casa — o gate conjuntivo NAO foi")
        print("         avaliado. (painel.py sem --json?)")
        return

    print(f"\n{'='*62}\nPOR CASA — a outra metade do gate\n{'='*62}")
    print(f"  {'casa':<24}{na[:9]:>9}{nb[:9]:>9}{'A-B':>9}  IC 95%")
    perde = []
    for casa in comuns:
        a, b = casas_a[casa], casas_b[casa]
        ma, mb = statistics.mean(a), statistics.mean(b)
        d, lo, hi, _ = est.welch(ma, statistics.stdev(a), len(a),
                                 mb, statistics.stdev(b), len(b))
        quem = na if lo > 0 else nb if hi < 0 else None
        print(f"  {casa:<24}{100*ma:8.2f}%{100*mb:8.2f}%{100*d:+9.2f}"
              f"  [{100*lo:+.2f}; {100*hi:+.2f}]"
              + ("" if quem is None else f"  <- {quem[:16]}"))
        if vencedor and quem and quem != vencedor:
            perde.append(casa)

    if vencedor is None:
        print("\n  gate: nao se aplica — o agregado nao apontou vencedor.")
    elif perde:
        print(f"\n  gate: NAO PASSA. {vencedor} vence no agregado mas REGRIDE em")
        print(f"        {', '.join(perde)}.")
    else:
        print(f"\n  gate: PASSA. {vencedor} vence no agregado e nao regride em")
        print(f"        nenhuma das {len(comuns)} casas.")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="decks/ogerpon_v6.csv")
    ap.add_argument("--b", default="decks/ogerpon_v2.csv")
    ap.add_argument("--replicas", type=int, default=5)
    ap.add_argument("--n", type=int, default=1100)
    # Bonferroni pela FAMILIA declarada de testes, nao pelo que esta rodada
    # mede. O plano da Strategy declara cinco alteracoes de lista; o T1 teve o
    # intervalo corrigido a mao, e conta a mao e o proximo erro esperando.
    ap.add_argument("--familia", type=int, default=1,
                    help="quantos testes na familia (Bonferroni); 1 = sem correcao")
    # O protocolo de REPLICAS so existia para decks. Variantes do agente eram
    # medidas por `painel.py --variantes a,b`, que agrega as partidas num
    # binomial unico — e a auditoria de 14/08 mediu sobredispersao de 1,39x
    # nesse agregado, ou seja, IC 39% estreitos. Com estes dois argumentos a
    # mesma comparacao roda por REPLICAS, que e onde a dispersao real aparece.
    ap.add_argument("--variante-a", default="atual")
    ap.add_argument("--variante-b", default=None,
                    help="se dado, compara variantes do agente (mesmo deck)")
    args = ap.parse_args()

    var_a = args.variante_a
    var_b = args.variante_b or args.variante_a
    if args.variante_b:
        # comparando AGENTES: o deck tem de ser o mesmo dos dois lados, senao
        # a medicao mistura as duas causas — que e o acoplamento que este
        # projeto passou a semana medindo.
        args.b = args.a
        na, nb = var_a, var_b
    else:
        na = pathlib.Path(args.a).stem
        nb = pathlib.Path(args.b).stem
    print(f"{na} contra {nb} | {args.replicas} replicas de cada | "
          f"N={args.n} por casa\n")
    print("Alternando A, B, A, B... para que qualquer deriva da maquina se")
    print("distribua entre os dois em vez de virar diferenca sistematica.\n")

    va, vb = [], []
    casas_a: dict[str, list[float]] = collections.defaultdict(list)
    casas_b: dict[str, list[float]] = collections.defaultdict(list)
    t0 = time.time()
    for i in range(args.replicas):
        for deck, var, acc, casas, nome in ((args.a, var_a, va, casas_a, na),
                                            (args.b, var_b, vb, casas_b, nb)):
            p, por_casa = uma_rodada(deck, args.n, var)
            marca = f"{100*p:.2f}%" if p is not None else "FALHOU"
            acc.append(p) if p is not None else None
            for casa, taxa in por_casa.items():
                casas[casa].append(taxa)
            print(f"  replica {i+1}  {nome:<14} {marca:>8}"
                  f"   [{(time.time()-t0)/60:.0f} min]", flush=True)

    if len(va) < 2 or len(vb) < 2:
        print("\nreplicas insuficientes")
        return

    ma, mb = statistics.mean(va), statistics.mean(vb)
    sa = statistics.stdev(va)     # ddof=1: desvio AMOSTRAL
    sb = statistics.stdev(vb)

    # t de Welch, nao z. Com 5 replicas por lado o multiplicador correto e
    # ~2,49 contra 1,96 — o IC estava saindo 27% estreito demais. Welch (e nao
    # t comum) porque as variancias diferem de fato: na comparacao da capa,
    # 0,81pp de um lado contra 1,87pp do outro.
    d, lo, hi, df = est.welch(ma, sa, len(va), mb, sb, len(vb))
    se = math.sqrt(sa**2 / len(va) + sb**2 / len(vb))

    print(f"\n{'='*62}\nRESULTADO\n{'='*62}")
    print(f"  {na:<16} {100*ma:6.2f}% +- {100*sa:.2f}pp   (n={len(va)})")
    print(f"  {nb:<16} {100*mb:6.2f}% +- {100*sb:.2f}pp   (n={len(vb)})")
    print(f"\n  diferenca : {100*d:+.2f}pp")
    print(f"  erro padrao: {100*se:.2f}pp   (Welch, {df:.1f} g.l.)")
    print(f"  IC 95%     : [{100*lo:+.2f}; {100*hi:+.2f}]")

    if args.familia > 1:
        _, lo_c, hi_c, _ = est.welch(ma, sa, len(va), mb, sb, len(vb),
                                     alfa=est.bonferroni(0.05, args.familia))
        print(f"  Bonferroni({args.familia}): [{100*lo_c:+.2f}; {100*hi_c:+.2f}]")
        lo, hi = lo_c, hi_c

    vencedor = na if lo > 0 else nb if hi < 0 else None
    if vencedor == na:
        print(f"\n  -> {na} e melhor no agregado. O IC nao cruza zero.")
    elif vencedor == nb:
        print(f"\n  -> {nb} e melhor no agregado. O IC nao cruza zero.")
    else:
        print("\n  -> EMPATE ESTATISTICO. O IC cruza zero — nao ha vencedor.")

    _por_casa(casas_a, casas_b, na, nb, vencedor)

    print(f"\n  tempo total: {(time.time()-t0)/60:.0f} min")
    print("\n  O `+-` vem da variacao ENTRE RODADAS (o engine nao aceita")
    print("  semente), nao do erro binomial de amostragem. O IC usa t de")
    print("  Welch: com poucas replicas, z subestima a largura.")


if __name__ == "__main__":
    main()
