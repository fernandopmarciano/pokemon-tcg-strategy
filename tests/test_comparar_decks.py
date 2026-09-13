"""Testes do gate CONJUNTIVO na comparacao de decks.

Por que existem: ate 18/08 o `comparar_decks.py` chamava o painel N vezes,
cada chamada media as quatro casas, e a funcao de leitura guardava so o
agregado. Metade do criterio de aceitacao do projeto — "nao regredir em
nenhuma casa" — era gerada e jogada fora a cada rodada.

O custo ja foi pago uma vez: o T1 (Lively Stadium) rodou 198 min e 88.000
partidas, ganhou no agregado, e mesmo assim nao pode ser adotado, porque o
recorte por casa nao existia mais quando a pergunta foi feita.

Estes testes prendem as duas coisas que teriam evitado isso:

  1. o contrato do `--json` entre painel.py e comparar_decks.py;
  2. a decisao do gate — em especial o caso que importa, "vence no agregado
     e REGRIDE numa casa", que e o unico motivo de o gate ser conjuntivo.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import comparar_decks as cd  # noqa: E402

CASAS = ["ref950+Lucario 0,05s", "ref950+Lucario 0,5s",
         "ref950+sample", "primeira (piso)"]


def _serie(base: float, n: int = 6) -> list[float]:
    """n replicas em torno de `base`, com dispersao pequena e realista.

    +-0,3 pp e a ordem de grandeza observada entre rodadas de 44.000
    partidas (0,58 a 0,67 pp no T1).
    """
    return [base + d for d in (-0.003, 0.002, -0.001, 0.003, -0.002, 0.001)][:n]


class TestContratoDoJson:
    """painel.py escreve, comparar_decks.py le. Se o formato mudar de um lado
    sem o outro, o gate volta a ficar sem dado — em silencio."""

    def test_le_taxa_por_casa(self, monkeypatch, tmp_path):
        def falso_run(cmd, **kwargs):
            caminho = cmd[cmd.index("--json") + 1]
            pathlib.Path(caminho).write_text(json.dumps(
                {"atual": {c: [550, 1100] for c in CASAS}}), encoding="utf-8")

            class R:
                stdout = "  atual   51.50%  <- base\n"
            return R()

        monkeypatch.setattr(cd.subprocess, "run", falso_run)
        agregado, por_casa = cd.uma_rodada("decks/x.csv", 1100)

        assert agregado == pytest.approx(0.515)
        assert set(por_casa) == set(CASAS)
        assert all(v == pytest.approx(0.5) for v in por_casa.values())

    def test_painel_sem_json_nao_derruba_a_rodada(self, monkeypatch):
        """Compatibilidade: o agregado continua saindo mesmo sem recorte."""
        def falso_run(cmd, **kwargs):
            class R:
                stdout = "  atual   49.00%  <- base\n"
            return R()

        monkeypatch.setattr(cd.subprocess, "run", falso_run)
        agregado, por_casa = cd.uma_rodada("decks/x.csv", 1100)

        assert agregado == pytest.approx(0.49)
        assert por_casa == {}

    def test_casa_com_n_zero_e_ignorada(self, monkeypatch):
        """Uma casa que falhou vem com n=0; dividir por ela e ZeroDivisionError."""
        def falso_run(cmd, **kwargs):
            caminho = cmd[cmd.index("--json") + 1]
            pathlib.Path(caminho).write_text(json.dumps(
                {"atual": {CASAS[0]: [550, 1100], CASAS[1]: [0, 0]}}),
                encoding="utf-8")

            class R:
                stdout = "  atual   50.00%  <- base\n"
            return R()

        monkeypatch.setattr(cd.subprocess, "run", falso_run)
        _, por_casa = cd.uma_rodada("decks/x.csv", 1100)

        assert list(por_casa) == [CASAS[0]]


class TestModoVariante:
    """O protocolo de replicas so existia para decks.

    Variantes do agente eram medidas por `painel.py --variantes a,b`, que
    agrega tudo num binomial unico — e a auditoria de 14/08 mediu
    sobredispersao de 1,39x ali, ou seja, IC 39% estreitos. Estes testes
    prendem os dois pontos em que o nome da variante entra: a chave do JSON e
    a regex do agregado. Errar qualquer um deles nao levanta excecao — devolve
    `None` e a replica some da amostra em silencio.
    """

    def _falso_run(self, nome_esperado, saida):
        def run(cmd, **kwargs):
            assert cmd[cmd.index("--variantes") + 1] == nome_esperado
            caminho = cmd[cmd.index("--json") + 1]
            pathlib.Path(caminho).write_text(json.dumps(
                {nome_esperado: {c: [572, 1100] for c in CASAS}}),
                encoding="utf-8")

            class R:
                stdout = saida
            return R()
        return run

    def test_le_a_variante_pedida(self, monkeypatch):
        monkeypatch.setattr(cd.subprocess, "run", self._falso_run(
            "t6_ataque75", "  t6_ataque75   52.00%  <- base\n"))
        agregado, por_casa = cd.uma_rodada("decks/v6.csv", 1100, "t6_ataque75")

        assert agregado == pytest.approx(0.52)
        assert por_casa[CASAS[0]] == pytest.approx(572 / 1100)

    def test_nome_de_outra_variante_nao_e_lido_por_engano(self, monkeypatch):
        """A regex antiga procurava `atual` fixo. Com outra variante ela cairia
        no ramo de emergencia e leria a ultima porcentagem da tela — que e a
        do bloco de gate, nao a do agregado."""
        saida = ("  atual         49.00%\n"
                 "  t6_ataque75   52.00%  <- base\n")
        monkeypatch.setattr(cd.subprocess, "run",
                            self._falso_run("t6_ataque75", saida))
        agregado, _ = cd.uma_rodada("decks/v6.csv", 1100, "t6_ataque75")

        assert agregado == pytest.approx(0.52)


class TestGateConjuntivo:
    def test_vence_em_tudo_passa(self, capsys):
        a = {c: _serie(0.50) for c in CASAS}
        b = {c: _serie(0.54) for c in CASAS}
        cd._por_casa(a, b, "v6", "candidato", "candidato")

        saida = capsys.readouterr().out
        assert "gate: PASSA" in saida
        assert "4 casas" in saida

    def test_regride_numa_casa_nao_passa(self, capsys):
        """O caso que justifica o gate existir: o agregado esconde uma casa.

        O candidato ganha 4 pp em tres casas e perde 4 pp na quarta. A media
        continua bem positiva; o gate tem de reprovar mesmo assim.
        """
        a = {c: _serie(0.50) for c in CASAS}
        b = {c: _serie(0.54) for c in CASAS}
        b[CASAS[2]] = _serie(0.46)          # a casa que desaba
        cd._por_casa(a, b, "v6", "candidato", "candidato")

        saida = capsys.readouterr().out
        assert "gate: NAO PASSA" in saida
        assert CASAS[2] in saida

    def test_casa_indistinguivel_nao_conta_como_regressao(self, capsys):
        """Ruido nao e regressao. Se o IC da casa cruza zero, ela nao reprova
        — senao qualquer candidato reprova por acaso em 4 casas."""
        a = {c: _serie(0.50) for c in CASAS}
        b = {c: _serie(0.54) for c in CASAS}
        b[CASAS[1]] = _serie(0.4995)        # praticamente empate
        cd._por_casa(a, b, "v6", "candidato", "candidato")

        saida = capsys.readouterr().out
        assert "gate: PASSA" in saida

    def test_empate_no_agregado_nao_avalia_o_gate(self, capsys):
        a = {c: _serie(0.50) for c in CASAS}
        b = {c: _serie(0.50) for c in CASAS}
        cd._por_casa(a, b, "v6", "candidato", None)

        assert "nao se aplica" in capsys.readouterr().out

    def test_sem_dado_por_casa_avisa_em_vez_de_calar(self, capsys):
        """O modo de falha antigo era SILENCIOSO: o gate simplesmente nao era
        avaliado e nada dizia isso."""
        cd._por_casa({}, {}, "v6", "candidato", "candidato")

        saida = capsys.readouterr().out
        assert "AVISO" in saida and "NAO foi" in saida

    def test_uma_replica_por_casa_nao_vira_desvio(self, capsys):
        """Com uma replica so nao ha desvio amostral; a casa e descartada em
        vez de estourar StatisticsError."""
        a = {c: [0.50] for c in CASAS}
        b = {c: [0.54] for c in CASAS}
        cd._por_casa(a, b, "v6", "candidato", "candidato")

        assert "AVISO" in capsys.readouterr().out
