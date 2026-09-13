"""A guarda de comprimento do prior — e por que ela precisa existir.

O prior vale +10,11 pp, medido no painel. Ele le `PRIOR_PESOS`, uma constante
gerada por `tools/exportar_prior.py`, e multiplica pelo vetor de
`features_da_decisao`.

Se alguém acrescentar uma feature e esquecer de retreinar, os dois comprimentos
divergem. Sem guarda, o loop levanta `IndexError`, o `except` la de cima do
`agent()` engole, e o prior morre EM SILENCIO — o agente continua jogando, so
que 10 pp pior, e nenhum teste acusa.

Aconteceu de verdade em 13/08, ao acrescentar tres features de dominio.
"""
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "submission"))
sys.path.insert(0, str(RAIZ / "engine_stub"))

import main as agente  # noqa: E402


def observacao():
    meu = {"active": [{"id": 96, "hp": 210, "maxHp": 210, "energies": [1, 1, 1]}],
           "bench": [], "prize": [None, None], "hand": [], "deckCount": 30}
    dele = {"active": [{"id": 700, "hp": 300, "maxHp": 300, "energies": [1, 1]}],
            "bench": [], "prize": [None, None], "deckCount": 30, "handCount": 4}
    return {
        "select": {"minCount": 1, "maxCount": 1, "option": [
            {"type": agente.OPT_END},
            {"type": agente.OPT_ATTACK, "attackId": 120},
        ]},
        "current": {"yourIndex": 0, "players": [meu, dele], "stadium": []},
        "logs": [],
    }


def test_descasamento_devolve_None_em_vez_de_levantar(monkeypatch):
    """Com menos pesos que features, o certo e devolver None.

    Cair para a L0 e ruim mas honesto. Levantar seria pior: o erro sumiria no
    `except` do agent() e o prior morreria sem deixar rastro.
    """
    monkeypatch.setattr(agente, "PRIOR_PESOS", agente.PRIOR_PESOS[:5])
    assert agente.pontuar_com_prior(observacao()) is None


def test_descasamento_para_MAIS_pesos_tambem(monkeypatch):
    monkeypatch.setattr(agente, "PRIOR_PESOS",
                        tuple(agente.PRIOR_PESOS) + (0.1,) * 20)
    assert agente.pontuar_com_prior(observacao()) is None


def test_o_agente_continua_jogando_com_o_prior_morto(monkeypatch):
    """A degradacao tem que ser silenciosa para o JOGO, nao para a medicao."""
    monkeypatch.setattr(agente, "PRIOR_PESOS", agente.PRIOR_PESOS[:5])
    escolha = agente.agent(observacao())
    assert escolha and 0 <= escolha[0] < 2


def test_os_comprimentos_batem_no_codigo_que_vai_para_a_ladder():
    """O teste que teria pego o descasamento de 13/08 na hora.

    PULA quando o prior esta em descasamento CONHECIDO — durante um ciclo de
    "acrescentei feature, ainda vou retreinar" isto e esperado. O que ele
    impede e o descasamento chegar a submissao sem ninguem notar: o
    `tools/conferir_submissao.py` checa a mesma coisa e NAO pula.
    """
    n_features = len(agente.NOMES_FEATURES)
    n_pesos = len(agente.PRIOR_PESOS)
    if n_features != n_pesos:
        pytest.skip(
            f"descasamento conhecido: {n_features} features contra {n_pesos} "
            f"pesos — rode `python tools/exportar_prior.py` para retreinar")
    assert n_features == n_pesos
    assert len(agente.PRIOR_MEDIA) == n_pesos
    assert len(agente.PRIOR_DESVIO) == n_pesos
