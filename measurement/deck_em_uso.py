"""Qual deck estamos jogando? Uma resposta, e ela se descobre sozinha.

## O problema que isto resolve

Oito ferramentas tinham o deck cravado no `default` do `--deck`: quatro em
`ogerpon_v2.csv` e quatro em `ogerpon_v1.csv`. O deck em uso e o **v6** desde
13/08. Rodar qualquer uma delas **sem** passar `--deck` media a lista errada, e
o resultado saia com cara de resultado.

Isso nao e hipotetico: e a **regua quebrada nº 5**, a que ja custou 6,7 pp e
escondeu o valor real do prior por 6x — a busca determinizava com um deck que
nao estava em jogo. A Parte 5.3 do plano-mestre listava estes defaults como
"a regua quebrada nº 5 esperando para acontecer de novo", e em 18/08 o TODO do
proprio projeto caiu nela: mandava rodar o painel sem `--deck-a`, que usaria o
deck do sample.

## Por que DESCOBRIR e nao cravar de novo

Trocar `v2` por `v6` nos oito arquivos resolveria hoje e quebraria de novo no
v7. A fonte da verdade ja existe e e inequivoca: **`submission/deck.csv` e a
lista que o agente embarca**. Esta funcao acha qual arquivo de `decks/` tem
exatamente aquele conteudo.

Se nenhum bater — a lista embarcada foi editada a mao, por exemplo — devolve o
proprio `submission/deck.csv`, que continua sendo a verdade. Nunca devolve um
palpite.
"""
from __future__ import annotations

import functools
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def _normalizar(texto: str) -> str:
    """Compara conteudo, nao bytes: fim de linha CRLF/LF nao pode decidir."""
    return "\n".join(l.strip() for l in texto.strip().splitlines() if l.strip())


@functools.lru_cache(maxsize=1)
def deck_em_uso(raiz: pathlib.Path | None = None) -> str:
    """Caminho relativo do deck que o agente embarca.

    Devolve `submission/deck.csv` se nenhuma lista de `decks/` corresponder —
    e isso e um sinal para investigar, nao um erro a esconder.
    """
    base = raiz or RAIZ
    embarcado = base / "submission" / "deck.csv"
    if not embarcado.exists():
        return "submission/deck.csv"
    alvo = _normalizar(embarcado.read_text(encoding="utf-8"))
    iguais = [c for c in sorted((base / "decks").glob("*.csv"))
              if _normalizar(c.read_text(encoding="utf-8")) == alvo]
    if not iguais:
        return "submission/deck.csv"

    # Mais de um arquivo pode ter o mesmo conteudo: quando um experimento e
    # PROMOVIDO, `ogerpon_t1_lively.csv` e `ogerpon_v7.csv` ficam identicos, e
    # a ordem alfabetica devolveria o nome do experimento. O canonico e o
    # VERSIONADO, e entre versionados vence o maior numero.
    versionados = [(int(m.group(1)), c) for c in iguais
                   if (m := re.fullmatch(r"ogerpon_v(\d+)\.csv", c.name))]
    escolhido = max(versionados)[1] if versionados else iguais[0]
    return f"decks/{escolhido.name}"
