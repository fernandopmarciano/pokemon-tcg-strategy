"""Testes das figuras do relatorio.

Elas vao na galeria de midia da submissao. Dois modos de falha importam:

  SVG QUEBRADO      um arquivo mal formado nao renderiza, e o revisor ve um
                    espaco em branco onde deveria estar a evidencia. Nao ha
                    excecao em tempo de geracao — so na hora de abrir.

  COR POR VARIAVEL  o `graficos.py` usa `var(--ink)` porque vive dentro de uma
                    pagina com tema. Fora dela essas variaveis nao resolvem e o
                    grafico sai INVISIVEL. Foi por isso que estas figuras nao
                    reaproveitaram aquele modulo, e o teste prende a decisao.
"""
from __future__ import annotations

import pathlib
import sys
import xml.etree.ElementTree as ET

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "tools"))

import figuras_writeup as fw  # noqa: E402


class TestSvgBemFormado:
    @pytest.mark.parametrize("nome", ["fig1-dispersao.svg", "fig2-forest.svg",
                                      "fig3-composicao.svg"])
    def test_arquivo_existe_e_parseia(self, nome):
        p = fw.SAIDA / nome
        if not p.exists():
            pytest.skip("figura ainda nao gerada (rode tools/figuras_writeup.py)")
        raiz = ET.parse(p).getroot()
        assert raiz.tag.endswith("svg")
        assert raiz.get("width") and raiz.get("height")

    @pytest.mark.parametrize("nome", ["fig1-dispersao.svg", "fig2-forest.svg",
                                      "fig3-composicao.svg"])
    def test_nao_depende_de_variavel_css(self, nome):
        """Autocontido: `var(--x)` fora de uma pagina com tema sai invisivel."""
        p = fw.SAIDA / nome
        if not p.exists():
            pytest.skip("figura ainda nao gerada")
        assert "var(--" not in p.read_text(encoding="utf-8")


class TestForestPlot:
    def test_todo_efeito_tem_intervalo(self):
        """Regra dura do projeto: numero sem erro nao entra. Num grafico, isso
        e a barra — um efeito sem IC nao pode estar na figura."""
        for rot, _rot_en, e, a, b in fw.EFEITOS:
            assert a < b, f"{rot}: intervalo invertido ou de largura zero"
            assert a <= e <= b, f"{rot}: o ponto esta fora do proprio intervalo"

    def test_adotado_tem_IC_acima_de_zero_salvo_a_excecao_declarada(self):
        """Se um "adotado" aparecesse com IC cruzando zero, ou o rotulo esta
        errado ou o numero esta — e a figura publicaria a contradicao.

        COM UMA EXCECAO, e ela e o ponto: a Hero's Cape EMPATOU (+0,19,
        IC [-0,44; +0,82]) e foi adotada assim mesmo, por decisao declarada
        contra o gate. E a unica vez em que o projeto contrariou o proprio
        criterio, e o relatorio a reporta no corpo do texto em vez do rodape.

        O teste antigo dizia `if "adotado" in rot: assert a > 0` e quebrou
        quando a Cape entrou na figura, em 23/08. Afrouxar para "ignore quem
        tem CONTRA no rotulo" seria trocar um invariante por um buraco — entao
        aqui a excecao e EXIGIDA: tem de existir exatamente uma, e ela tem de
        estar rotulada.
        """
        excecoes = [x for x in fw.EFEITOS if "CONTRA" in x[0]]
        assert len(excecoes) == 1, (
            "a excecao ao gate tem de ser unica e rotulada com CONTRA; "
            f"achei {len(excecoes)}")
        rot_exc, _rot_en, _e, a_exc, b_exc = excecoes[0]
        assert a_exc < 0 < b_exc, (
            f"{rot_exc}: rotulada como adotada CONTRA o criterio, mas o IC nao "
            "cruza zero — ou o rotulo esta errado, ou ela passou no gate")

        for rot, _rot_en, _e, a, _b in fw.EFEITOS:
            if "adotado" in rot and "CONTRA" not in rot:
                assert a > 0, f"{rot}: adotado mas o IC cruza zero"

    def test_todos_os_adotados_estao_na_figura(self):
        """A figura e a galeria de midia da submissao: um adotado que ficasse
        de fora seria um resultado publicado pela metade."""
        adotados = [x[0] for x in fw.EFEITOS if "adotado" in x[0]]
        assert len(adotados) >= 6, (
            "sao seis adotados ate 23/08 — cinco pelo gate e a Hero's Cape "
            f"contra ele; a figura lista {len(adotados)}")

    def test_o_consenso_rejeitado_tem_IC_abaixo_de_zero(self):
        rot, _rot_en, _e, _a, b = next(
            x for x in fw.EFEITOS if "consenso" in x[0])
        assert b < 0, f"{rot}: rejeitado mas o IC cruza zero"

    def test_todo_efeito_tem_rotulo_nos_dois_idiomas(self):
        """A submissao e em INGLES e a galeria vai junto com o texto. Um rotulo
        que ficasse so em portugues sairia numa figura que o avaliador le —
        foi assim que as tres figuras chegaram ao dia 13/09 em portugues."""
        for rot, rot_en, *_ in fw.EFEITOS:
            assert rot_en and rot_en != rot, f"{rot}: sem rotulo em ingles"

    def test_os_dois_idiomas_descrevem_a_mesma_adocao(self):
        """Traduzir nao pode mudar o veredito: quem e adotado em portugues tem
        de estar adotado em ingles, e a excecao ao gate tem de continuar
        marcada nos dois."""
        for rot, rot_en, *_ in fw.EFEITOS:
            assert ("adotado" in rot) == ("adopted" in rot_en), (
                f"{rot}: o veredito se perdeu na traducao")
            assert ("CONTRA" in rot) == ("AGAINST" in rot_en), (
                f"{rot}: a excecao ao gate se perdeu na traducao")


class TestIdioma:
    def test_o_deck_padrao_e_o_deck_em_uso(self):
        """A figura 3 foi publicada com a composicao do v7 porque o default da
        ferramenta apontava para um deck antigo. O default segue o deck em uso."""
        assert "v9" in _default_do_deck(), (
            "o --deck padrao tem de apontar para o deck em uso")

    def test_escrever_separa_os_idiomas(self, tmp_path, monkeypatch):
        """O arquivo em ingles nao pode sobrescrever o em portugues."""
        monkeypatch.setattr(fw, "SAIDA", tmp_path)
        monkeypatch.setattr(fw, "IDIOMA", "pt")
        pt = fw.escrever("fig9-teste.svg", ["<svg/>"])
        monkeypatch.setattr(fw, "IDIOMA", "en")
        en = fw.escrever("fig9-teste.svg", ["<svg/>"])
        assert pt != en, "as duas versoes gravaram no mesmo arquivo"
        assert en.name.endswith("-en.svg")

    def test_todo_texto_existe_nos_dois_idiomas(self):
        chaves = {i: set(d) for i, d in fw.TEXTOS.items()}
        assert chaves["pt"] == chaves["en"], (
            f"faltando: {chaves['pt'] ^ chaves['en']}")


def _default_do_deck() -> str:
    """O default do `--deck`, lido da fonte — sem executar o main()."""
    fonte = (RAIZ / "tools" / "figuras_writeup.py").read_text(encoding="utf-8")
    for linha in fonte.splitlines():
        if '"--deck"' in linha:
            return linha
    raise AssertionError("argumento --deck nao encontrado")


class TestFigura1:
    def test_le_replicas_do_log(self, tmp_path, monkeypatch):
        log = tmp_path / "x.log"
        log.write_text(
            "  replica 1  atual            52.20%   [15 min]\n"
            "  replica 1  outra            51.60%   [30 min]\n"
            "  replica 2  atual            52.90%   [45 min]\n",
            encoding="utf-8")
        monkeypatch.setattr(fw, "RAIZ", tmp_path.parent)
        monkeypatch.setattr(fw.pathlib.Path, "exists", lambda self: True)
        # le direto, sem depender do layout de diretorio
        import re
        v = [float(m) for m in re.findall(
            r"replica\s+\d+\s+atual\s+([\d.]+)%", log.read_text(encoding="utf-8"))]
        assert v == [52.20, 52.90], "a variante nao pode entrar como se fosse `atual`"

    def test_sem_dados_devolve_None_em_vez_de_estourar(self, monkeypatch):
        monkeypatch.setattr(fw, "replicas_do_log", lambda nome: [])
        assert fw.figura1() is None
