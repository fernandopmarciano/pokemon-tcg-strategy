"""Testes contra opcoes REAIS extraidas de episodios da ladder.

Motivo de existir: os 312 testes de `test_agent.py` rodam contra o
`engine_stub`, que foi escrito por engenharia reversa antes de haver dados. O
stub supunha `option.type` como string e um campo `text` — os dois errados. Com
isso, `score_options` dava a MESMA nota para todas as opcoes em 100% das 3.041
decisoes reais medidas, e o agente virava "escolhe a primeira opcao legal" sem
que teste nenhum acusasse.

A fixture `decisoes_reais.json` sao 105 decisoes de partidas de verdade, uma ou
duas por combinacao de tipos observada. Ver docs/api-real.md.
"""
import json
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "submission"))
sys.path.insert(0, str(RAIZ / "engine_stub"))

import main as agente  # noqa: E402

FIXTURE = pathlib.Path(__file__).parent / "fixtures" / "decisoes_reais.json"


@pytest.fixture(scope="module")
def decisoes():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_fixture_tem_opcoes_com_tipo_inteiro(decisoes):
    """Guarda o fato que quebrou o agente: o tipo e int, nunca string."""
    assert decisoes, "fixture vazia"
    for d in decisoes:
        for o in d["option"]:
            assert isinstance(o["type"], int), f"tipo nao-inteiro: {o!r}"


def test_heuristica_diferencia_a_maioria_das_decisoes(decisoes):
    """O teste que teria pego a regressao original.

    Nao exige 100%: pares binarios (tipos 1 e 2) e confirmacoes sem campo
    nenhum sao estruturalmente indistinguiveis, e desempatar esses casos exige
    o contexto do State. Exige que a heuristica nao seja constante no geral.
    """
    indiferentes = 0
    for d in decisoes:
        notas = agente.score_options(d["option"])
        assert len(notas) == len(d["option"])
        if len(set(notas)) == 1:
            indiferentes += 1
    fracao = indiferentes / len(decisoes)
    assert fracao < 0.25, (
        f"heuristica indiferente em {fracao:.0%} das decisoes reais — "
        "sinal de que score_options voltou a nao ler o esquema real"
    )


def test_selecao_e_sempre_legal_em_decisoes_reais(decisoes):
    """O nucleo select_indices sobre entradas reais, nao sinteticas."""
    for d in decisoes:
        notas = agente.score_options(d["option"])
        mn = d.get("minCount") or 1
        mx = d.get("maxCount") or 1
        escolha = agente.select_indices(notas, mn, mx)
        assert mn <= len(escolha) <= mx, f"tamanho ilegal: {escolha}"
        assert len(set(escolha)) == len(escolha), f"indices duplicados: {escolha}"
        assert all(0 <= i < len(d["option"]) for i in escolha), f"fora do range: {escolha}"


def test_ataque_tem_prioridade_sobre_confirmar():
    """Ordem de prioridade basica, com os tipos reais."""
    opcoes = [{"type": agente.OPT_END}, {"type": agente.OPT_ATTACK, "attackId": 154}]
    notas = agente.score_options(opcoes)
    assert notas[1] > notas[0]


def test_primeira_chamada_devolve_o_deck():
    """O contrato do container: `select` None => devolver os 60 Card IDs.

    Custou a submissao S1 (08/08, ERROR). A arena local nao exercita este
    caminho porque `battle_start` ja recebe os decks; so o container chama o
    agente para montar a partida.
    """
    resposta = agente.agent({"select": None, "current": None, "logs": []})
    assert len(resposta) == 60, f"esperado 60 Card IDs, veio {len(resposta)}"
    assert all(isinstance(i, int) for i in resposta)


def test_sem_select_nenhum_tambem_devolve_deck():
    """Robustez: a chave pode vir ausente em vez de None."""
    assert len(agente.agent({"current": None})) == 60


def test_carrega_sem_dunder_file():
    """O container executa o agente com `exec(code, env)` e NAO define __file__.

    Custou tres submissoes (S2, S3, S4 em 08/08): `load_deck` resolvia o caminho
    por __file__, o import levantava NameError e a submissao voltava
    SubmissionStatus.ERROR sem log nenhum.

    Este teste executa o modulo exatamente como o kaggle_environments faz.
    """
    import os

    codigo = (RAIZ / "submission" / "main.py").read_text(encoding="utf-8")
    ambiente = {"__name__": "__main__"}  # sem __file__, de proposito
    cwd = os.getcwd()
    try:
        os.chdir(RAIZ / "submission")
        exec(compile(codigo, "main.py", "exec"), ambiente)
    finally:
        os.chdir(cwd)
    assert "agent" in ambiente, "o modulo nao definiu agent()"
    assert callable(ambiente["agent"])
