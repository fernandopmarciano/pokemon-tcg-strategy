"""Quantas palavras tem o writeup? A resposta depende da convencao — entao mostra todas.

## Por que isto existe

A Strategy tem limite de **2.000 palavras**, e o rascunho carregava a afirmacao
de que tinha "1.993 palavras contando prosa, tabelas e legendas". O numero era
uma **estimativa escrita a mao**, e nao reproduzia: recontado, o mesmo arquivo
da entre 1.686 e 2.289 palavras dependendo do que se conta.

Estimativa perto de um limite rigido e a mesma familia de erro que o projeto ja
catalogou em medicao: **o que nao e medido nao e resultado**. Um limite de
submissao merece um contador, nao uma lembranca.

## As convencoes, e por que quatro e nao uma

Nao se sabe como o Kaggle conta. As quatro linhas cercam o intervalo:

| convencao | inclui |
|---|---|
| **tudo** | prosa, tabelas, titulos, citacoes — o **teto**, e o numero para planejar |
| sem titulos | tira `#` |
| so prosa | tira as tabelas inteiras |
| so prosa nua | tira tabelas, titulos e citacoes — o **piso** |

**Planeje pelo teto.** Se o teto couber, qualquer convencao cabe.

## O que nao conta como palavra

Separadores de tabela (`|---|---:|`), reguas horizontais (`---`) e marcacao de
enfase (`*`, `_`, backticks). Links viram o texto visivel: `[a](url)` conta como
`a`. Um token so conta se tiver pelo menos uma letra ou digito — assim `—` e
`|` ficam de fora.

Uso:
    python tools/contar_palavras.py docs/relatorio/RASCUNHO-v2.md --limite 2000
"""
from __future__ import annotations

import argparse
import pathlib
import re

SEPARADOR_TABELA = re.compile(r"\|?[\s\|:\-]+\|?")
REGUA = re.compile(r"-{3,}")

# Bloco que NAO vai na submissao — nota de revisao, historico de versao. Fica no
# arquivo porque e util para quem revisa, e sai da conta porque o Kaggle nunca
# vai ve-lo. Marcar e melhor que apagar: o limite passa a valer sobre o texto
# que sera de fato enviado.
FORA = re.compile(r"<!--\s*NAO-SUBMISSAO\s*-->.*?<!--\s*/NAO-SUBMISSAO\s*-->",
                  re.S)


def palavras(texto: str, *, tabelas: bool = True, titulos: bool = True,
             citacoes: bool = True) -> list[str]:
    linhas = []
    for linha in texto.splitlines():
        t = linha.strip()
        if "|" in t and SEPARADOR_TABELA.fullmatch(t):
            continue
        if REGUA.fullmatch(t):
            continue
        if not tabelas and t.startswith("|"):
            continue
        if not titulos and t.startswith("#"):
            continue
        if not citacoes and t.startswith(">"):
            continue
        linhas.append(t)

    txt = "\n".join(linhas)
    txt = re.sub(r"^#+\s*", "", txt, flags=re.M)
    txt = re.sub(r"^>\s?", "", txt, flags=re.M)
    txt = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", txt)
    txt = txt.replace("|", " ")
    txt = re.sub(r"[*_`~]", "", txt)
    return [w for w in re.split(r"\s+", txt) if re.search(r"[0-9A-Za-zÀ-ÿ]", w)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", type=pathlib.Path)
    ap.add_argument("--limite", type=int, default=2000)
    args = ap.parse_args()

    bruto = args.arquivo.read_text(encoding="utf-8")
    s, cortados = FORA.subn("", bruto)
    fora = len(palavras(bruto)) - len(palavras(s))
    casos = [
        ("tudo (prosa + tabelas + titulos + citacoes)", {}),
        ("sem titulos", {"titulos": False}),
        ("so prosa (sem tabelas)", {"tabelas": False}),
        ("so prosa nua", {"tabelas": False, "titulos": False,
                          "citacoes": False}),
    ]

    print(f"\n  {args.arquivo}  —  limite {args.limite}")
    if cortados:
        print(f"  ({cortados} bloco(s) NAO-SUBMISSAO fora da conta: "
              f"{fora} palavras)")
    print()
    print(f"  {'convencao':<44}{'palavras':>10}{'folga':>10}")
    print("  " + "-" * 64)
    teto = 0
    for rotulo, kw in casos:
        n = len(palavras(s, **kw))
        teto = max(teto, n)
        folga = args.limite - n
        marca = "" if folga >= 0 else "   ESTOURA"
        print(f"  {rotulo:<44}{n:>10}{folga:>+10}{marca}")

    print(f"""
  PLANEJE PELO TETO: {teto} palavras. Sobra {args.limite - teto:+d}.
  {"Cabe em qualquer convencao." if teto <= args.limite else
   f"NAO CABE — e preciso cortar {teto - args.limite} palavras para caber em"
   " qualquer convencao."}""")


if __name__ == "__main__":
    main()
