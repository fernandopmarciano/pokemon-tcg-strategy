"""Os intervalos do projeto, feitos como a literatura manda.

Auditoria de 14/08. O projeto tinha a disciplina de sempre reportar erro — mas
o METODO estava errado em quatro pontos, e um deles afirmava certeza onde nao
havia nenhuma.

O caso grave: `0 de 16 decks derrubam o Ogerpon com a capa` foi publicado como
**0,0% +/- 0,0pp**. O intervalo de Wald tem largura ZERO quando k=0 — ele
"prova" que nenhum deck do universo derruba, a partir de 16 observacoes. O
intervalo correto (Wilson) e [0; 19,4%], e a regra de tres da o mesmo recado:
com 16 observacoes e nenhum evento, ate ~19% continua compativel com o dado.

Isso importava: o argumento da capa se apoiou nesse zero.

As quatro correcoes:

  1. WILSON no lugar de WALD para proporcao. Brown, Cai & DasGupta (2001),
     "Interval Estimation for a Binomial Proportion", mostram que o Wald tem
     cobertura pessima e erratica mesmo com n grande, e e indefensavel perto
     de 0 e de 1. O painel.py ja usava Wilson; as analises novas usaram Wald a
     mao — um metodo pior do que o que o proprio repositorio oferecia.

  2. t DE STUDENT no lugar de z para media de REPLICAS. Com 5 replicas por
     lado, o multiplicador correto e t(Welch) ~ 2,49, nao z = 1,96: o
     intervalo estava 27% estreito demais.

  3. BONFERRONI ao comparar muitas hipoteses. Nove entraram no painel esta
     semana. A 5% cada, esperar ~0,45 falso-positivo e o que o acaso entrega.

  4. O ARGUMENTO DO SINAL ("as 4 casas subiram, 1/16") nao vale: as casas
     compartilham agente, codigo e deck, entao nao sao independentes. E mesmo
     supondo independencia, o teste de sinal com n=4 da p = 0,0625, que nao e
     significativo a 5%.

Consequencia da (3), e ela muda uma afirmacao ja publicada: a politica de
estadio, reportada como "piora de verdade, IC exclui zero", PERDE a
significancia sob correcao — [-6,59; +0,81]. O deck v6 SOBREVIVE
([+1,60; +2,88]), que e o unico resultado em que agimos.
"""
from __future__ import annotations

import math
from statistics import NormalDist

Z95 = NormalDist().inv_cdf(0.975)


def z_para(alfa: float) -> float:
    return NormalDist().inv_cdf(1 - alfa / 2)


def wilson(k: int, n: int, alfa: float = 0.05) -> tuple[float, float, float]:
    """(proporcao, baixo, alto) pelo escore de Wilson.

    Nunca sai de [0, 1] e nunca colapsa para largura zero — as duas falhas do
    Wald que motivaram esta funcao.
    """
    if n <= 0:
        return 0.0, 0.0, 1.0
    z = z_para(alfa)
    p = k / n
    d = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / d
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, centro - meia), min(1.0, centro + meia)


def regra_de_tres(n: int) -> float:
    """Limite superior aproximado quando ZERO eventos foram observados.

    Com n observacoes e nenhum evento, o teto de 95% e ~3/n. E a leitura de
    bolso do caso k=0, e o antidoto ao "0,0% +/- 0,0pp".
    """
    return 3.0 / n if n > 0 else 1.0


def _t_critico(df: float, alfa: float = 0.05) -> float:
    """t de Student sem scipy, por expansao de Cornish-Fisher.

    Erro abaixo de 1% para df >= 3, que cobre qualquer numero de replicas que
    este projeto consiga rodar.
    """
    if df <= 0:
        return float("inf")
    z = z_para(alfa)
    return z * (1 + (z * z + 1) / (4 * df)
                + (5 * z ** 4 + 16 * z * z + 3) / (96 * df * df))


def welch(media_a: float, dp_a: float, n_a: int,
          media_b: float, dp_b: float, n_b: int,
          alfa: float = 0.05) -> tuple[float, float, float, float]:
    """Diferenca de duas medias com variancias e n possivelmente diferentes.

    Devolve (diferenca, baixo, alto, graus_de_liberdade).

    Welch em vez de t pareado porque o engine nao aceita semente: nao existe
    partida pareada entre os dois lados, so amostras independentes. E Welch em
    vez de t comum porque as variancias diferem de fato — na comparacao da
    capa, 0,81pp contra 1,87pp.
    """
    va, vb = dp_a ** 2 / max(n_a, 1), dp_b ** 2 / max(n_b, 1)
    se = math.sqrt(va + vb)
    if se == 0:
        return media_a - media_b, 0.0, 0.0, float("inf")
    num = (va + vb) ** 2
    den = (va ** 2 / max(n_a - 1, 1)) + (vb ** 2 / max(n_b - 1, 1))
    df = num / den if den > 0 else float("inf")
    t = _t_critico(df, alfa)
    d = media_a - media_b
    return d, d - t * se, d + t * se, df


def diferenca_de_proporcoes(k1: int, n1: int, k2: int, n2: int,
                            alfa: float = 0.05
                            ) -> tuple[float, float, float]:
    """(diferenca, baixo, alto) para p1 - p2, por Newcombe.

    Newcombe (1998) combina os intervalos de Wilson de cada lado em vez de
    usar o erro padrao de Wald da diferenca. Mantem a cobertura quando alguma
    das proporcoes esta perto de 0 ou 1 — que e onde o metodo ingenuo falha.
    """
    p1, l1, h1 = wilson(k1, n1, alfa)
    p2, l2, h2 = wilson(k2, n2, alfa)
    d = p1 - p2
    baixo = d - math.sqrt((p1 - l1) ** 2 + (h2 - p2) ** 2)
    alto = d + math.sqrt((h1 - p1) ** 2 + (p2 - l2) ** 2)
    return d, baixo, alto


def bonferroni(alfa: float, m: int) -> float:
    """Alfa corrigido para m comparacoes.

    Conservador de proposito. Um projeto que testa nove hipoteses por semana e
    so reporta o IC de 95% de cada uma esta contando com ~0,45 falso-positivo
    por semana como se fosse descoberta.
    """
    return alfa / max(m, 1)


def formatar(p: float, lo: float, hi: float, *, pct=True) -> str:
    """`34,0% [30,4; 37,8]` — o formato que o documento usa."""
    f = 100.0 if pct else 1.0
    s = "%" if pct else ""
    return (f"{p*f:.1f}{s} [{lo*f:.1f}; {hi*f:.1f}]").replace(".", ",")


if __name__ == "__main__":
    print("O caso que motivou este modulo — 0 de 16:")
    p, lo, hi = wilson(0, 16)
    print(f"  Wilson       : {formatar(p, lo, hi)}")
    print(f"  regra de tres: ate {100*regra_de_tres(16):.1f}%")
    print("  Wald         : 0,0% [0,0; 0,0]  <- largura zero, e foi o publicado")
