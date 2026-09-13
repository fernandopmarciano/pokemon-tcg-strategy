"""Confere TUDO que uma submissao precisa, antes de gastar um slot.

Sao 5 submissoes por dia e elas devolvem UMA PALAVRA. O projeto ja perdeu
quatro para bugs que nenhum teste local pegava. Esta lista existe para que
nenhuma delas se repita.

O que confere, e por que cada item esta aqui:

  1. o main.py carrega SEM __file__          custou 3 submissoes (S2, S3, S4)
  2. a primeira chamada devolve os 60 IDs    custou 1 submissao (S1)
  3. o deck e valido e aceito pelo engine
  4. o deck do pacote == o deck que medimos
  5. TODA flag experimental esta DESLIGADA   nenhuma passou no painel
  6. os pesos sao os que passaram no painel
  7. o pacote tem main.py, deck.csv e cg/
  8. o main.py do pacote e byte a byte o do submission/
  9. nada no pacote depende de arquivo de fora

Uso:
    python tools/conferir_submissao.py --deck decks/ogerpon_v2.csv
"""
from __future__ import annotations

import argparse
import hashlib
import os
import pathlib
import re
import subprocess
import sys
import tarfile

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
from deck_em_uso import deck_em_uso  # noqa: E402

ok_geral = True

# ---------------------------------------------------------------------------
# O QUE O AGENTE TEM QUE VALER NO DIA DA SUBMISSAO — todas as flags, sem excecao.
#
# Por que a lista e DERIVADA da fonte e nao escrita a mao: em 26/08 o checklist
# conferia 6 flags de 26. Vinte e uma passavam sem ninguem olhar, entre elas
# HP_INVARIANTE (que o T13 adotou) e as duas do T14. Uma flag experimental nova,
# esquecida ligada, teria embarcado calada.
#
# Agora a ferramenta LE as flags do main.py e exige que cada uma esteja aqui.
# Flag nova sem valor declarado = FALHA no checklist, ate alguem decidir com que
# valor ela vai para a ladder. Nao da para esquecer o que a lista cobra.
VALORES_DE_SUBMISSAO = {
    # o motor
    "TIME_BUDGET_S": (2.0, "orcamento por decisao; a mediana real e 2 ms"),
    "PLY": (1, "2 ply piora 4,9 pp"),
    "LARGURA_FEIXE": (0, "o feixe foi reprovado, -0,76 pp"),
    "USAR_META_PRIOR": (True, "determinizar o deck DELE pelo meta, nao pelo nosso"),
    # a escada de prioridades — T6
    "PRIO_ABILITY": (46.0, "T6"),
    "PRIO_ATTACH": (50.0, "T6"),
    "COMPRESSAO_PRIORIDADE": (1.0, "T6"),
    "COMPRESSAO_ATAQUE": (0.5, "T6: compressao de ATTACK/END, +1,03 pp"),
    # a avaliacao de estado
    "W_HP": (1.0, "peso da vida"),
    "HP_INVARIANTE": (1, "T13 ADOTADO: dano do campo, invariante a rotacao, +0,59 pp"),
    "W_ENERGIA": (15.0, "energia no ativo"),
    "W_AMEACA": (2.0, "ameaca+energia, +1,25 pp"),
    "W_LETAL": (1000.0, "morrer no proximo turno custa os premios que valemos"),
    "W_DECKOUT": (50.0, "deck acabando"),
    # ATENCAO: os +10,11 pp sao de 12/08, medidos no painel aposentado em
    # 22/08. Remedido em 01-03/09 com comparar_decks.py, o efeito fica entre
    # -0,80 e +0,27 pp (docs/testes/r1-r2-remedicoes-da-auditoria-2026-09-01).
    # O valor 10.0 continua sendo o esperado no pacote porque o agente esta
    # congelado desde 16/08 — o checklist confere o que FOI submetido.
    "W_PRIOR": (10.0, "prior ligado; efeito remedido: -0,80 a +0,27 pp"),
    # reprovadas ou nao adotadas — todas DESLIGADAS
    "USAR_DANO_REAL": (False, "-11,46 pp"),
    "USAR_DANO_FRACAO": (False, "-7,37 pp; reaberto no T15, ainda nao adotado"),
    "USAR_AMEACA_FRAQUEZA": (False, "nao passou"),
    "USAR_VITORIA_IMEDIATA": (False, "+0,23 pp, nao passou"),
    "USAR_PROTECAO": (False, "+0,56 pp, nao passou"),
    "USAR_ARVORES": (False, "destilar as arvores: -0,40 pp"),
    "W_ARVORES": (1.0, "inerte enquanto USAR_ARVORES estiver desligado"),
    "UTILIDADE_CARTA": (False, "P1 aposentada: mudava 0,5% das decisoes"),
    "_POLITICA_ENV": ("0", "as sete regras de carta: +0,09 pp"),
    "ENERGIA_DO_ALVO": (False, "T14a: reprovada POR CONSTRUCAO, desestimula nocautear"),
    "BANCO_DELE": (False, "T14b: empate, +0,10 pp [-0,30; +0,49]"),
    "ENERGIA_DELE_CONTRA": (False, "T16: empate (+0,10 pp), nao adotado"),
}

_FLAG_NA_FONTE = re.compile(
    r'''^([A-Z_][A-Z0-9_]*)\s*=\s*.*?os\.environ\.get\(\s*["'](PTCG_[A-Z0-9_]+)["'].*$''',
    re.M)


def flags_declaradas_na_fonte(codigo: str) -> dict[str, str]:
    """Toda constante do agente que nasce de uma variavel de ambiente."""
    return {m.group(1): m.group(2) for m in _FLAG_NA_FONTE.finditer(codigo)}



def check(cond: bool, titulo: str, detalhe: str = "") -> bool:
    global ok_geral
    marca = "OK  " if cond else "FALHA"
    print(f"  [{marca}] {titulo}")
    if detalhe:
        print(f"          {detalhe}")
    if not cond:
        ok_geral = False
    return cond


def secao(t: str) -> None:
    print(f"\n{'=' * 74}\n{t}\n{'=' * 74}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", default=deck_em_uso())
    args = ap.parse_args()
    deck_src = RAIZ / args.deck
    pacote = RAIZ / "build" / f"{deck_src.stem}.tar.gz"

    # ------------------------------------------------------------ 1 e 2
    secao("1-2. O CONTRATO DO CONTAINER")
    codigo = (RAIZ / "submission" / "main.py").read_text(encoding="utf-8")
    amb = {"__name__": "__main__"}  # sem __file__, como o kaggle_environments
    cwd = os.getcwd()
    try:
        os.chdir(RAIZ / "submission")
        exec(compile(codigo, "main.py", "exec"), amb)
        carregou = True
        erro = ""
    except Exception as e:  # pragma: no cover
        carregou, erro = False, repr(e)
    finally:
        os.chdir(cwd)
    check(carregou, "main.py carrega SEM __file__", erro)

    if carregou:
        deck_devolvido = amb["agent"]({"select": None, "logs": [],
                                       "current": None})
        check(len(deck_devolvido) == 60,
              "a primeira chamada devolve os 60 Card IDs",
              f"devolveu {len(deck_devolvido)}")

    # ------------------------------------------------------------- 3 e 4
    secao("3-4. O DECK")
    ids = [int(x) for x in deck_src.read_text(encoding="utf-8")
           .replace(",", "\n").split() if x.strip()]
    check(len(ids) == 60, f"{args.deck} tem 60 cartas", f"{len(ids)}")
    r = subprocess.run([sys.executable, "tools/validar_deck.py", args.deck],
                       capture_output=True, text=True, cwd=str(RAIZ),
                       encoding="utf-8", errors="replace")
    check("engine: aceitou a lista" in (r.stdout or ""),
          "o engine aceita a lista")
    sub_deck = [int(x) for x in (RAIZ / "submission" / "deck.csv")
                .read_text(encoding="utf-8").replace(",", "\n").split()
                if x.strip()]
    check(sorted(sub_deck) == sorted(ids),
          "submission/deck.csv == o deck medido",
          "sem isto, a determinizacao local usa outra lista")

    # ----------------------------------------------------------------- 5
    secao("5. AS 26 FLAGS DO AGENTE — a lista sai da FONTE, nao da memoria")
    m = amb
    na_fonte = flags_declaradas_na_fonte(codigo)
    check(bool(na_fonte), f"o main.py declara {len(na_fonte)} flags de ambiente")

    # A checagem que impede o esquecimento: flag nova sem valor declarado FALHA.
    # Antes disto, o checklist olhava 6 de 26 e as outras 20 embarcavam no escuro.
    sem_valor = sorted(set(na_fonte) - set(VALORES_DE_SUBMISSAO))
    check(not sem_valor,
          "toda flag da fonte tem valor de submissao declarado",
          ("DECLARE em VALORES_DE_SUBMISSAO: " + ", ".join(sem_valor))
          if sem_valor else f"{len(na_fonte)} conferidas, nenhuma solta")
    fantasma = sorted(set(VALORES_DE_SUBMISSAO) - set(na_fonte))
    check(not fantasma,
          "nenhum valor declarado sobrou para flag que nao existe mais",
          ", ".join(fantasma) if fantasma else "")

    for nome in sorted(na_fonte):
        if nome not in VALORES_DE_SUBMISSAO:
            continue
        esperado, motivo = VALORES_DE_SUBMISSAO[nome]
        v = m.get(nome)
        # `==` e nao `is`: 1 e True passam pelo mesmo teste e o tipo vem do
        # int()/float()/bool() de cada linha. O que importa e o VALOR embarcado.
        igual = (v == esperado) and (isinstance(v, bool) == isinstance(esperado, bool))
        check(igual, f"{nome} = {esperado!r}", f"{motivo} (esta {v!r})")

    # ----------------------------------------------------------------- 6
    secao("6. O QUE NAO VEM DE VARIAVEL DE AMBIENTE")
    # Os pesos e flags de ambiente ja foram na secao 5, um por um. Aqui fica o
    # que nenhuma variavel controla e que quebra em silencio.
    check(m.get("USAR_L1") is True, "USAR_L1 = True",
          f"a escada L1c e o agente (esta {m.get('USAR_L1')})")
    # NAO e um numero fixo: e a igualdade. Acrescentar uma feature sem
    # retreinar faz `pontuar_com_prior` devolver None pela guarda, o agente cai
    # para a L0 e perde os +10,11pp — em silencio. Aqui isso vira FALHA.
    n_feat = len(m.get("NOMES_FEATURES") or ())
    n_pesos = len(m.get("PRIOR_PESOS") or ())
    check(n_feat == n_pesos and n_pesos > 0,
          "o prior tem um peso por feature",
          f"{n_feat} features contra {n_pesos} pesos — se divergirem, o prior "
          f"morre calado. Rode tools/exportar_prior.py")
    check(len(m.get("PRIOR_MEDIA") or ()) == n_pesos
          and len(m.get("PRIOR_DESVIO") or ()) == n_pesos,
          "media e desvio tem o mesmo comprimento dos pesos")

    # --------------------------------------------------------------- 7-9
    secao("7-9. O PACOTE")
    if not check(pacote.exists(), f"{pacote.relative_to(RAIZ)} existe"):
        print("\n  rode: python tools/empacotar.py " + args.deck)
    else:
        with tarfile.open(pacote) as t:
            nomes = t.getnames()
            check("main.py" in nomes, "o pacote tem main.py")
            check("deck.csv" in nomes, "o pacote tem deck.csv")
            check(any(n.startswith("cg/") for n in nomes),
                  "o pacote tem a pasta cg/",
                  "faltar cg/ causou 3 ERROR em 08/08")
            # BYTES, nao texto. A primeira versao comparava
            # `read_text()` (que normaliza CRLF para LF) contra os bytes crus
            # do tar, e acusava FALHA em dois arquivos identicos. O verificador
            # tinha um bug da mesma classe que ele existe para pegar: comparar
            # duas coisas que parecem iguais e nao foram medidas do mesmo jeito.
            pk_main = t.extractfile("main.py").read()
            disco = (RAIZ / "submission" / "main.py").read_bytes()
            check(hashlib.sha256(pk_main).hexdigest()
                  == hashlib.sha256(disco).hexdigest(),
                  "o main.py do pacote e IDENTICO ao de submission/",
                  f"{len(pk_main)} bytes contra {len(disco)}")
            pk_deck = [int(x) for x in
                       t.extractfile("deck.csv").read().decode().split()]
            check(sorted(pk_deck) == sorted(ids),
                  "o deck.csv do pacote e o deck medido")
            check("prior_antigo" not in nomes,
                  "prior_antigo.py NAO vai no pacote",
                  "ele e so para medicao; o import e opcional e protegido")

    secao("VEREDITO")
    print("  TUDO PRONTO PARA SUBMETER" if ok_geral else
          "  NAO SUBMETA — ha item em FALHA acima")
    print("\n  Proximo passo obrigatorio pela regra do projeto:")
    print("    python kaggle/diagnostico/gerar.py " + args.deck)
    print("    cd kaggle/diagnostico && kaggle kernels push -p .")
    print("  Kernels sao ilimitados e devolvem traceback; submissoes sao 5/dia")
    print("  e devolvem uma palavra.")
    sys.exit(0 if ok_geral else 1)


if __name__ == "__main__":
    main()
