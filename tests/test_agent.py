"""Testes do agente heuristico — foco nas INVARIANTES verificaveis offline.

O que estes testes GARANTEM (sem o engine real): o agente sempre devolve uma selecao LEGAL
(sem duplicatas, indices no range, tamanho em [minCount, maxCount]), nunca lanca excecao, e
respeita a ordem de prioridade heuristica basica. O que NAO validam: forca real do agente em
partidas (isso exige o engine cabt oficial).
"""
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine_stub"))   # stub do cg
sys.path.insert(0, str(ROOT / "submission"))     # main.py

import main  # noqa: E402


# ---------- Nucleo select_indices: invariantes ----------
def _assert_legal(sel, n, min_count, max_count):
    assert isinstance(sel, list)
    assert len(sel) == len(set(sel)), "sem duplicatas"
    assert all(0 <= i < n for i in sel), "indices no range"
    eff_max = min(max_count, n)
    eff_min = min(min_count, eff_max)
    assert eff_min <= len(sel) <= eff_max, f"tamanho em [{eff_min},{eff_max}]"


def test_single_select_pega_o_melhor():
    scores = [1.0, 9.0, 3.0]
    assert main.select_indices(scores, 1, 1) == [1]


def test_optional_passa_quando_nada_bom():
    # min=0: so escolhe se score>0; todos <=0 -> passa (vazio)
    assert main.select_indices([-1.0, 0.0], 0, 1) == []


def test_optional_pega_melhor_quando_positivo():
    assert main.select_indices([-1.0, 5.0, 2.0], 0, 1) == [1]


def test_multi_exato_pega_top_k():
    sel = main.select_indices([5.0, 1.0, 9.0, 2.0], 2, 2)
    assert sorted(sel) == [0, 2]  # os dois maiores


def test_maxcount_maior_que_opcoes_clampa():
    sel = main.select_indices([1.0, 2.0], 1, 5)  # so ha 2 opcoes
    _assert_legal(sel, 2, 1, 5)


def test_sem_opcoes_retorna_vazio():
    assert main.select_indices([], 1, 1) == []


@pytest.mark.parametrize("seed", range(200))
def test_invariante_aleatoria(seed):
    """Property-based: para configuracoes aleatorias, a selecao e SEMPRE legal."""
    rng = random.Random(seed)
    n = rng.randint(0, 8)
    scores = [rng.uniform(-5, 100) for _ in range(n)]
    max_count = rng.randint(0, 6)
    min_count = rng.randint(0, max_count) if max_count else 0
    sel = main.select_indices(scores, min_count, max_count)
    _assert_legal(sel, n, min_count, max_count)


# ---------- agent(): sempre legal, nunca quebra ----------
def _mk_obs(options, min_count=1, max_count=1):
    return {"select": {"option": options, "minCount": min_count, "maxCount": max_count},
            "current": None, "logs": []}


def test_agent_selecao_legal_basica():
    obs = _mk_obs([{"type": main.OPT_ATTACK, "attackId": 154}, {"type": main.OPT_END}])
    sel = main.agent(obs)
    _assert_legal(sel, 2, 1, 1)


def test_agent_prefere_atacar_a_passar():
    obs = _mk_obs([{"type": main.OPT_END}, {"type": main.OPT_ATTACK}])
    assert main.agent(obs) == [1]  # ataca (indice 1), nao confirma


def test_agent_sem_opcoes():
    assert main.agent(_mk_obs([])) == []


def test_agent_nunca_lanca_com_lixo():
    # obs malformado nao pode quebrar o agente (fallback legal)
    for bad in [{}, {"select": {}}, {"select": {"option": [1, 2, 3]}}, None]:
        sel = main.agent(bad if bad is not None else {})
        assert isinstance(sel, list)


@pytest.mark.parametrize("seed", range(100))
def test_agent_invariante_aleatoria(seed):
    rng = random.Random(seed + 1000)
    n = rng.randint(0, 7)
    types = [main.OPT_ATTACK, main.OPT_END, main.OPT_PLAY, main.OPT_ATTACH,
             main.OPT_ABILITY, main.OPT_RETREAT, main.OPT_EVOLVE]
    options = [{"type": rng.choice(types)} for _ in range(n)]
    max_count = rng.randint(1, 4) if n else 1
    min_count = rng.randint(0, max_count)
    sel = main.agent(_mk_obs(options, min_count, max_count))
    _assert_legal(sel, n, min_count, max_count)


# ---------- Integracao com o stub (all_card_data real) ----------
def test_all_card_data_carrega():
    """Precisa do CSV oficial, que NAO e versionado (nao pode ser redistribuido).

    Sem ele, `all_card_data()` do stub devolve vazio — e isso e correto, nao um
    defeito. O teste PULA em vez de falhar: num clone limpo (o caso do CI) o
    arquivo nao existe, e falhar ali esconderia as falhas de verdade.
    """
    from cg.api import all_card_data
    cards = all_card_data()
    if not cards:
        pytest.skip("data/EN_Card_Data.csv ausente — baixe da competicao "
                    "(ver data/README.md)")
    assert len(cards) > 1000
    assert all("id" in c and "name" in c for c in list(cards.values())[:20])


def test_score_ataque_nao_usa_mais_dano_da_carta():
    """O bonus por dano saiu, e isso e proposital.

    A opcao de ataque real traz `attackId`, nao o id da carta: identificar o
    Pokemon exige cruzar `area`+`index` com o State, que `score_options` nao
    recebe. O teste antigo passava porque o stub inventava um `card_id` na
    opcao. Fica registrado como divida: reintroduzir o bonus quando existir a
    tabela attackId -> dano (ver docs/api-real.md).
    """
    s = main.score_options([{"type": main.OPT_ATTACK, "attackId": 10},
                            {"type": main.OPT_ATTACK, "attackId": 900}])
    assert len(s) == 2
    assert all(x > 0 for x in s)