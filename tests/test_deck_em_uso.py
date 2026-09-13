"""O deck que as ferramentas medem quando ninguem passa `--deck`.

Por que existe: oito ferramentas tinham a lista cravada no default — quatro em
`ogerpon_v2.csv`, quatro em `ogerpon_v1.csv` — enquanto o deck em uso e o v6
desde 13/08. Rodar sem `--deck` media a lista errada, e o resultado saia com
cara de resultado.

E a **regua quebrada nº 5**, a que custou 6,7 pp e escondeu o valor do prior por
6x. O plano-mestre a listava como "esperando para acontecer de novo", e em 18/08
o TODO do proprio projeto caiu nela.

Cravar "v6" nos oito arquivos resolveria hoje e quebraria no v7. Por isso o
default passou a ser `deck_em_uso()`, que descobre a lista comparando com
`submission/deck.csv` — a que o agente realmente embarca — e os testes abaixo
proibem que alguem volte a escrever um deck a mao ali.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))
sys.path.insert(0, str(RAIZ / "submission"))
sys.path.insert(0, str(RAIZ / "engine_stub"))

from deck_em_uso import _normalizar, deck_em_uso  # noqa: E402

FERRAMENTAS = [
    "analisar_deck", "avaliar_deck_vs_meta", "conferir_submissao",
    "diagnosticar_derrotas", "medir_override", "medir_regras",
    "medir_teal_dance", "medir_uso_cartas",
]


class TestResolucao:
    def test_encontra_a_lista_que_o_agente_embarca(self):
        caminho = deck_em_uso()
        assert (RAIZ / caminho).exists()
        embarcado = (RAIZ / "submission" / "deck.csv").read_text(encoding="utf-8")
        assert _normalizar((RAIZ / caminho).read_text(encoding="utf-8")) \
            == _normalizar(embarcado)

    def test_fim_de_linha_nao_decide(self):
        """CRLF contra LF nao pode fazer a resolucao falhar — o repo roda no
        Windows com autocrlf, e um byte a mais viraria 'nenhum deck bate'."""
        assert _normalizar("a,1\r\nb,2\r\n") == _normalizar("a,1\nb,2")

    def test_experimento_promovido_devolve_o_NOME_VERSIONADO(self, tmp_path):
        """Quando um experimento e promovido, dois arquivos ficam identicos.

        Aconteceu com o T1 em 18/08: `ogerpon_t1_lively.csv` virou
        `ogerpon_v7.csv` e a ordem alfabetica devolvia o nome do experimento —
        as ferramentas diriam estar medindo `t1_lively` quando o canonico e o
        v7. O versionado ganha, e entre versionados vence o maior numero.
        """
        (tmp_path / "decks").mkdir()
        (tmp_path / "submission").mkdir()
        conteudo = "id,qtd\n1,4\n2,2\n"
        for nome in ("ogerpon_t1_lively.csv", "ogerpon_v7.csv",
                     "ogerpon_v6.csv"):
            (tmp_path / "decks" / nome).write_text(conteudo, encoding="utf-8")
        (tmp_path / "submission" / "deck.csv").write_text(
            conteudo, encoding="utf-8")

        deck_em_uso.cache_clear()
        try:
            assert deck_em_uso(tmp_path) == "decks/ogerpon_v7.csv"
        finally:
            deck_em_uso.cache_clear()

    def test_sem_versionado_cai_no_que_existe(self, tmp_path):
        (tmp_path / "decks").mkdir()
        (tmp_path / "submission").mkdir()
        conteudo = "id,qtd\n9,1\n"
        (tmp_path / "decks" / "experimento_x.csv").write_text(
            conteudo, encoding="utf-8")
        (tmp_path / "submission" / "deck.csv").write_text(
            conteudo, encoding="utf-8")

        deck_em_uso.cache_clear()
        try:
            assert deck_em_uso(tmp_path) == "decks/experimento_x.csv"
        finally:
            deck_em_uso.cache_clear()

    def test_sem_deck_embarcado_devolve_a_fonte_da_verdade(self, tmp_path):
        """Nunca devolve um palpite: se nao da para descobrir, aponta para o
        arquivo que o agente carrega e deixa o problema visivel."""
        deck_em_uso.cache_clear()
        try:
            assert deck_em_uso(tmp_path) == "submission/deck.csv"
        finally:
            deck_em_uso.cache_clear()


class TestDefaultsDasFerramentas:
    """Verificacao ESTATICA, de proposito.

    A primeira versao destes testes importava cada ferramenta e espiava o
    `ArgumentParser`. Passava sozinha e quebrava na suite inteira: os outros
    testes ja tinham importado `cg` do `engine_stub`, entao o `import
    cg.game` das ferramentas falhava — `sys.modules` ja estava decidido.

    Ler a fonte nao depende de ordem de importacao, nao precisa do engine
    oficial, e testa exatamente o que se quer proibir: **um deck escrito a mao
    no default**.
    """

    @pytest.mark.parametrize("nome", FERRAMENTAS)
    def test_default_nao_e_deck_cravado(self, nome):
        fonte = (RAIZ / "tools" / f"{nome}.py").read_text(encoding="utf-8")
        linhas = [l.strip() for l in fonte.splitlines()
                  if '"--deck"' in l and "add_argument" in l]
        assert linhas, f"{nome} nao tem --deck"
        for linha in linhas:
            assert "decks/ogerpon" not in linha, (
                f"{nome} tem deck cravado no default: {linha}")
            assert "deck_em_uso()" in linha, (
                f"{nome} nao resolve o deck em uso: {linha}")

    @pytest.mark.parametrize("nome", FERRAMENTAS)
    def test_importa_o_resolvedor(self, nome):
        fonte = (RAIZ / "tools" / f"{nome}.py").read_text(encoding="utf-8")
        assert "from deck_em_uso import deck_em_uso" in fonte
