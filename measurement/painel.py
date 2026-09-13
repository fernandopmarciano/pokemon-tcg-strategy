"""O gate: nenhuma mudanca entra sem vencer um PAINEL de oponentes.

Por que existe: duas vezes nesta sessao uma regua unica enganou a medicao.
Primeiro `primeira`, que esta ~500 pontos de rating abaixo do campo. Depois o
ref950 jogando o deck do SAMPLE — as heuristicas dele tem IDs do deck de
Lucario cravados, entao com outra lista ele vira uma parede. O sinal de que
algo estava errado: dar 10x mais tempo de busca ao adversario nos fazia
MELHORAR (53,6% a 0,05 s contra 55,5% a 0,5 s). Com o deck dele, o numero real
e 15,7%.

O painel:

  ref950 + Lucario, 0,05 s   o oponente mais forte disponivel
  ref950 + Lucario, 0,5 s    o mesmo com mais busca — o par detecta regua boba
  ref950 + sample            politica forte, deck desencaixado
  primeira                   o piso; se cair aqui, algo quebrou

Resultado por oponente E agregado. Uma variante so e melhor se ganhar no
agregado E nao regredir em nenhuma casa alem do ruido.

Uso:
    python tools/painel.py --variantes rollout,feixe4 --n 900 --replicas 3
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import estatistica as est  # noqa: E402

RAIZ = pathlib.Path(__file__).resolve().parents[1]

# (rotulo, agente, deck do oponente, budget)
PAINEL_BASE = [
    ("ref950+Lucario 0,05s", "ref950", "decks/ref950_lucario.csv", 0.05),
    ("ref950+Lucario 0,5s", "ref950", "decks/ref950_lucario.csv", 0.5),
    ("ref950+sample", "ref950", None, 0.05),
    ("primeira (piso)", "primeira", None, 0.05),
]

# Casas de META — **NAO SAO GATE**. Leia isto antes de usar.
#
# Motivo de existirem: nenhuma das quatro casas acima e um arquetipo do campo.
# O painel testa contra o deck de Lucario de um agente publico e contra o deck
# do sample — duas listas que ninguem joga na ladder. E 26,5% do campo mata o
# Ogerpon (210 HP) de um golpe, contra 0% do painel.
#
# Motivo de NAO servirem como gate, medido depois de construidas:
#
#   nos (l1c + Ogerpon) contra           win rate nosso
#   ref950 + Kangaskhan                          98,5%
#   ref950 + Grimmsnarl                          95,0%
#   ref950 + Lopunny                             93,5%
#   l0     + Kangaskhan                          99,7%
#
# E a MESMA regua quebrada que o projeto ja documentou duas vezes: as
# heuristicas do ref950 tem os IDs do deck de Lucario cravados, e com outra
# lista ele vira parede. A l0 nao pilota estas listas melhor. Os decks do meta
# sao complexos (linhas de Estagio 2, energia especial); o nosso e simples de
# proposito — foi o criterio do estudo de deck. Entao estas casas medem "deck
# simples bem pilotado contra deck complexo mal pilotado", que e verdade e e
# inutil.
#
# O override de protecao disparou ZERO vezes em 2.910 decisoes contra o
# Kangaskhan aqui: as partidas terminam antes de ele montar a ameaca.
#
# PARA QUE SERVEM: exploracao e o mapa de ameacas estatico
# (tools/avaliar_deck_vs_meta.py, que e conta de carta e nao precisa de piloto).
# NAO decida nada pelo agregado destas casas.
#
# -------------------------------------------------------------------------
# 23/08 — a tentativa de conserto, e ela FALHOU. Leia antes de tentar de novo.
#
# A ideia parecia obvia: o `ref950` esta preso por IDs cravados, mas o `l1c` nao
# tem carta nenhuma cravada (busca, avalia estado, tabelas de dano GERADAS do
# catalogo para 1.004 cartas). Logo ele pilotaria qualquer lista, e estas casas
# passariam a medir matchup contra ~70% do campo. Entrou tambem o Dragapult, que
# e o maior arquetipo (20,1%) e nao estava aqui.
#
# ⚠ NAO FUNCIONOU, e o aviso ja estava escrito acima: "A l0 nao pilota estas
# listas melhor" — com 99,7% contra o Kangaskhan. Os controles de 23/08 so
# confirmaram e quantificaram:
#
#   espelho (nosso deck dos dois lados)          49,5% [47,8; 51,3]  <- ok
#   Dragapult pilotado pela POLITICA NULA        99,7%
#   Dragapult pilotado pelo l1c                  99,0%
#
# Todo o valor do nosso agente pilotando deck alheio e 0,7 pp sobre escolher
# sempre a primeira opcao. Trocamos uma regua quebrada por outra da mesma
# familia: o ref950 e preso por IDs cravados, o l1c e preso pela AVALIACAO, que
# foi construida em cima do Ogerpon (W_ENERGIA premia acumulo, o banco vale
# zero, e nao ha termo nenhum para linha de evolucao).
#
# FICAM FORA DO GATE, e nao servem nem para explorar matchup. Ficam registradas
# para que ninguem tente o mesmo conserto de novo.
# Ver docs/meta-nao-mede-2026-08-23.md.
PAINEL_META = [
    ("meta Dragapult 20%", "l1c", "decks/meta_dragapult_ex.csv", 0.5),
    ("meta Grimmsnarl 15%", "l1c", "decks/meta_marnie_s_grimmsnarl_ex.csv", 0.5),
    ("meta Alakazam 15%", "l1c", "decks/meta_alakazam.csv", 0.5),
    ("meta Kangaskhan 12%", "l1c", "decks/meta_mega_kangaskhan_ex.csv", 0.5),
    ("meta Lopunny 13%", "l1c", "decks/meta_mega_lopunny_ex.csv", 0.5),
]

PAINEL = list(PAINEL_BASE)

# Cada variante e um conjunto de variaveis de ambiente sobre o main.py.
VARIANTES = {
    "rollout": {"PTCG_FEIXE": "0"},
    "feixe4": {"PTCG_FEIXE": "4"},
    "feixe8": {"PTCG_FEIXE": "8"},
    "feixe4_ply2": {"PTCG_FEIXE": "4", "PTCG_PLY": "2"},
    "determ_ordem": {"PTCG_FEIXE": "4", "PTCG_DETERMINIZACAO": "ordem"},
    # Pesos por ORDEM DE GRANDEZA, derivados dos que ja existem — nao por
    # tuning. W_PREMIO=1000 por premio, entao morrer custa premios x 1000.
    # W_DANO=2,0 para o dano que causamos, entao 2,0 para o que vamos tomar.
    # Tunar antes de saber se o termo ganha e otimizar ruido.
    "ameaca": {"PTCG_W_AMEACA": "2.0", "PTCG_W_LETAL": "1000",
               "PTCG_W_DECKOUT": "50"},
    "ameaca_energia": {"PTCG_W_AMEACA": "2.0", "PTCG_W_LETAL": "1000",
                       "PTCG_W_DECKOUT": "50", "PTCG_W_ENERGIA": "15"},
    # `atual` = o que esta na ladder (ameaca+energia ligadas, prior LIGADO).
    #
    # ⚠ CORRIGIDO em 28/08: esta linha dizia "prior desligado" e estava errada.
    # `atual` = {} nao sobrescreve nada, e o padrao do main.py e W_PRIOR = 10.0
    # (main.py:3320). O mesmo erro estava no CONTINUAR-AQUI. Confirmado
    # importando o modulo: W_PRIOR em uso = 10.0, 50 pesos carregados.
    # Os dois pesos do prior sao PRE-DEFINIDOS, nao varridos: a escala da
    # BASE_PRIORITY vai de 8 a 62 e os logits do prior de -1,4 a +0,2, entao
    # W=3 reordena dentro de uma faixa e W=10 atravessa faixas. Varrer e depois
    # escolher o melhor seria o jardim de caminhos que se bifurcam.
    "atual": {},
    # 22/08 — as duas frentes do documento `onde-esta-o-ganho`.
    #
    # P2: a energia no banco deixa de valer o mesmo que a do ativo. O Myriad
    # conta a energia dos DOIS ATIVOS, e o Teal Dance anexa A SI MESMO — entao
    # a habilidade do banco poe a energia do turno em quem nao vai atacar, e a
    # avaliacao dava a MESMA nota aos dois estados. Medido: 23,7% dos turnos
    # comecam pelo banco. Os dois valores sao pre-definidos (metade e nada),
    # nao varridos, e o segundo faz papel de controle.
    "p2_banco_meio": {"PTCG_FRACAO_ENERGIA_BANCO": "0.5"},
    "p2_banco_zero": {"PTCG_FRACAO_ENERGIA_BANCO": "0.0"},
    # ADOTADO em 23/08: o padrao virou 0,0, entao `atual` JA E o banco_zero.
    # Esta variante guarda o comportamento ANTIGO, para quem precisar refazer a
    # comparacao sem garimpar o historico do git.
    "p2_banco_um_antigo": {"PTCG_FRACAO_ENERGIA_BANCO": "1.0"},
    # A POLITICA COMO ELA ESTAVA EM 15/08 — a ultima submissao a ladder.
    # Desde entao dois parametros mudaram por medicao: o T6 levou a compressao
    # de 0,0 para 0,5 (+1,03 pp) e o T10 levou a fracao do banco de 1,0 para
    # 0,0 (+0,88 pp). Esta variante desfaz os dois de uma vez, e serve para
    # perguntar o que nunca foi perguntado: os ganhos SOMAM?
    #
    # ⚠ CORRIGIDO em 28/08 — esta variante DEIXOU de reproduzir 15/08 sozinha.
    # Quando o T13 foi adotado (25/08), o padrao de PTCG_HP_INVARIANTE virou
    # "1" no main.py:2009. Como esta variante nao fixava a flag, ela passou a
    # herdar o T13 LIGADO nos dois lados da comparacao — e quem reexecutasse o
    # T12 hoje mediria so T6+T10, chamando o resultado de "ganho sobre o agente
    # da ladder". O numero sairia MENOR que o real, sem erro nenhum na tela.
    #
    # Consequencia para o relatorio: os +2,56 pp [+1,90; +3,22] do T12 sao de
    # 23/08 e NAO incluem o T13 (+0,59 pp, adotado em 25/08). O ganho real
    # sobre a politica da ladder e maior que o numero publicado.
    "politica_15_08": {"PTCG_COMPRESSAO_ATAQUE": "0.0",
                       "PTCG_FRACAO_ENERGIA_BANCO": "1.0",
                       "PTCG_HP_INVARIANTE": "0"},
    # T13 — o termo de vida deixa de pagar por trocar de Pokemon. Ver o bloco
    # HP_INVARIANTE no main.py: hoje recuar um ativo machucado vale +75 na
    # avaliacao, e atacar vale zero a menos que nocauteie. Medido: atacamos
    # 2,5x menos e recuamos 3,2x mais que pilotos >= 1.000, nas MESMAS posicoes.
    "t13_hp_invariante": {"PTCG_HP_INVARIANTE": "1"},
    # a REPLICA do T13, com a outra formula invariante ao recuo
    "t13b_vida_do_campo": {"PTCG_HP_INVARIANTE": "2"},
    # a replica DE VERDADE do T13: mesma formula, peso pela metade
    "t13c_peso_meio": {"PTCG_HP_INVARIANTE": "1", "PTCG_W_HP": "0.5"},
    # T14 — o que a avaliacao nao ve do outro lado da mesa
    # t14a REPROVADA POR CONSTRUCAO — ver o comentario ENERGIA_DO_ALVO no
    # main.py. Fica registrada para nao ser reinventada.
    "t14a_energia_do_alvo": {"PTCG_ENERGIA_DO_ALVO": "1"},
    "t14b_banco_dele": {"PTCG_BANCO_DELE": "1"},
    # T15 — reabrir o dano num agente que mudou tres vezes desde a reprovacao
    "t15_dano_fracao": {"PTCG_DANO_FRACAO": "1"},
    # T16 — a energia dele conta CONTRA (sinal invertido do t14a)
    "t16_energia_dele_contra": {"PTCG_ENERGIA_DELE_CONTRA": "1"},
    # P1: utilidade por carta na SELECAO MULTIPLA — 16,6% das decisoes, em que
    # a busca nao roda e o que sobra e o prior posicional.
    "p1_utilidade": {"PTCG_UTILIDADE_CARTA": "1"},
    "prior3": {"PTCG_W_PRIOR": "3"},
    "prior10": {"PTCG_W_PRIOR": "10"},
    # Override de vitoria imediata. Nao tem peso para escolher: ou o ataque
    # fecha a partida ou nao fecha. Nada a varrer, nada a tunar.
    "vitoria": {"PTCG_VITORIA_IMEDIATA": "1"},
    # W_DANO deixa de valer zero. O peso NAO muda — ele ja existia em 2,0 e
    # nunca fez nada, porque `avaliar_estado` lia um campo `damage` que o
    # engine nao entrega. Mexer no peso agora seria trocar duas coisas de uma
    # vez e nao saber qual delas mediu.
    "dano_real": {"PTCG_DANO_REAL": "1"},
    # A mesma informacao, mas como FRACAO do HP vezes o proprio W_KO — assim
    # progresso contra o ativo dele nunca vale mais que derruba-lo. Foi o que
    # a versao absoluta violou, e o painel cobrou 11,46pp por isso.
    "dano_fracao": {"PTCG_DANO_FRACAO": "1"},
    "dano_fracao_vitoria": {"PTCG_DANO_FRACAO": "1", "PTCG_VITORIA_IMEDIATA": "1"},
    # Fraqueza/resistencia na ameaca. INERTE com o deck de agua: nenhum dos
    # seis arquetipos do meta cruza fraqueza com ele, nem em uma direcao nem na
    # outra. Fica registrada para o dia em que o deck mudar de tipo.
    "ameaca_fraqueza": {"PTCG_AMEACA_FRAQUEZA": "1"},
    # Salvar o ativo do nocaute. Nao tem peso: ou a carta muda o desfecho ou
    # nao muda. E barato porque nem Item nem Ferramenta encerram o turno.
    "protecao": {"PTCG_PROTEGER": "1"},
    # Politica por carta: da criterio a 8 cartas que so tinham a prioridade do
    # TIPO de opcao. Nao ha peso a varrer — cada regra e uma conta.
    "politica": {"PTCG_POLITICA_CARTA": "1"},
    "politica_protecao": {"PTCG_POLITICA_CARTA": "1", "PTCG_PROTEGER": "1"},
    # Cada regra SOZINHA. Um pacote que passa no gate nao diz quais regras
    # pagaram, e e provavel que alguma atrapalhe. O pre-teste
    # (tools/medir_regras.py) mede quantas jogadas cada uma muda por 100
    # partidas. A versao ANTIGA do `boss` ficou em 4,0 e por isso nao entrava
    # aqui — abaixo do limiar de ~5, o painel nao separa do ruido.
    "pol_lillies": {"PTCG_POLITICA_CARTA": "lillies"},   # muda 310/100
    "pol_judge": {"PTCG_POLITICA_CARTA": "judge"},       # muda 196/100
    "pol_ns_plan": {"PTCG_POLITICA_CARTA": "ns_plan"},   # muda 140/100
    "pol_estadio": {"PTCG_POLITICA_CARTA": "estadio"},   # muda 108/100
    "pol_scrapper": {"PTCG_POLITICA_CARTA": "scrapper"},  # muda 48/100
    "pol_briar": {"PTCG_POLITICA_CARTA": "briar"},       # muda 20/100
    # Regras reescritas em 14/08, cada uma a partir de uma medicao:
    #   cura     o Jumbo era jogado com 58% de chance de o Pokemon morrer
    #            mesmo assim, e 10% com menos de 20 de dano. A politica era
    #            sobre ENERGIA (o pre-requisito) e passou a ser sobre DANO.
    #   estadio  85,3% do campo joga estadio. Jogar cedo entrega o campo; a
    #            regra prioriza ANULAR o Nighttime Mine, o unico do meta que
    #            nos ataca (nosso Ogerpon e Tera e o ataque custaria +1).
    #   briar    uso de 43%, o menor do deck, e jogada com 3,7 premios
    #            faltando. Agora so vale se o ataque FECHA a partida.
    "pol_cura": {"PTCG_POLITICA_CARTA": "cura"},
    "pol_fechar": {"PTCG_POLITICA_CARTA": "cura,estadio,briar"},

    # BOSS'S ORDERS reescrito em 14/08, a partir da ideia do Fernando de puxar
    # a maior ameaca. A energia do ALVO e multiplicador do NOSSO dano (o Myriad
    # soma 30 por energia nos dois ativos), entao o carregado se entrega — mas
    # so ate onde da para mata-lo: os Mega de 300-340 PS exigem 5 a 7 energias
    # minhas mesmo cheios, e puxar sem matar entrega a posicao de ataque.
    # O criterio virou "consigo matar neste turno?".
    #
    # A regra antiga mudava 4,0 jogadas/100 partidas; a nova muda 13,3 — passou
    # a valer o painel.
    "pol_boss": {"PTCG_POLITICA_CARTA": "boss"},           # muda 13,3/100

    # COMPRESSAO DA ESCALA DE PRIORIDADE. O prior tem top-1 ZERO nas decisoes
    # em que a jogada certa e RECUAR — e nao por falta de modelo: o AUC dele
    # dentro dessas opcoes e 0,755, contra 0,768 de um especialista treinado so
    # nelas. Ele SABE e nao consegue agir, porque BASE_PRIORITY[EVOLVE]=62
    # contra BASE_PRIORITY[RETREAT]=18 e o prior so mexe ~17 pontos.
    #
    # Comprimir mantem a ORDEM da heuristica e encurta as distancias. Os
    # valores sao PRE-DEFINIDOS, nao varridos: 0,5 e a metade e 0,25 e o
    # quarto — ordens de grandeza, nao busca.
    "comprimir50": {"PTCG_COMPRESSAO": "0.5"},
    "comprimir25": {"PTCG_COMPRESSAO": "0.25"},

    # T6 — a compressao SELETIVA. A uniforme acima mexia nos quatro tipos, e a
    # medicao de 15/08 mostrou que so DOIS precisavam: a busca corrige ATTACH
    # (867) e ABILITY (644) e NAO corrige ATTACK (23) nem END (58), em 14.926
    # decisoes. Isso explica por que a uniforme encolheu de +2,03 para +0,91pp.
    #
    # Os dois valores sao PRE-DEFINIDOS pela conta, nao varridos: o prior move
    # ~17 pontos, entao para ter autoridade sobre PLAY(55)->ATTACK(12)=43 o
    # residual precisa caber em 17, o que exige S >= 0,68. O 0,50 fica de
    # proposito ABAIXO do limiar: se ele tambem mover o resultado, o mecanismo
    # proposto nao e o que esta agindo.
    "t6_ataque50": {"PTCG_COMPRESSAO_ATAQUE": "0.5"},
    "t6_ataque75": {"PTCG_COMPRESSAO_ATAQUE": "0.75"},
    # O resultado (19/08): as DUAS passaram, +1,10 e +1,03pp com gate conjuntivo.
    # E o 0,50 era o CONTROLE, fora do alcance do prior — passar igual
    # FALSIFICOU a explicacao. O que age e a REORDENACAO de tipos, nao a
    # distancia. Adotado o 0,50 como padrao, por parcimonia.

    # T7 — a fronteira ATTACH x PLAY. Perdemos 52,4% das decisoes de anexar para
    # o PLAY (55 contra 50), e o erro NAO e de alvo: quando decidimos anexar,
    # concordamos com o destino em 100%. E os pilotos fortes nao ordenam as duas
    # — mediana 0,38 e quartis identicos para ambas.
    #
    # Valores PRE-DEFINIDOS: 55,0 e o valor exato de PLAY (empata, e o desempate
    # cai para a posicao); 57,0 e o ponto medio entre PLAY(55) e EVOLVE(62).
    # A `attach_empata` e a PRIMARIA por corresponder ao observado.
    # Ver docs/t7-attach-contra-play-2026-08-19.md.
    "t7_attach_empata": {"PTCG_PRIO_ATTACH": "55.0"},
    "t7_attach_acima": {"PTCG_PRIO_ATTACH": "57.0"},
    # As duas melhores sozinhas, e as duas JUNTAS. A hipotese: elas se cancelam
    # porque disputam o mesmo slot — so se joga UM Apoiador por turno, entao
    # favorecer os dois ao mesmo tempo nao soma. Medido separado: +1,55 e
    # +1,13; no pacote de sete regras, +0,09.
    "pol_lillies_judge": {"PTCG_POLITICA_CARTA": "lillies,judge"},
    # O prior: `atual` usa os coeficientes retreinados em 12/08; estas duas sao
    # as referencias para saber se o retreino pagou.
    #
    # ⚠ AUDITORIA de 28/08 — o maior numero do agente esta medido na regua
    # aposentada. Os +10,11 pp do prior [+8,59; +11,64] sao de 12/08 e sairam
    # DO PAINEL; em 22/08 o painel foi aposentado para decidir variante de
    # agente (regua quebrada nº 9: partidas empilhadas, sobredispersao 1,39x,
    # IC 39% estreitos). A variante `sem_prior` existe desde entao e nunca foi
    # rodada no instrumento que substituiu o painel. O ponto deve sobreviver
    # (10 pp e ~11x a resolucao), mas o INTERVALO citado no relatorio vem da
    # regua que o proprio relatorio diz ser invalida.
    #
    #   python tools/comparar_decks.py --variante-a atual     #       --variante-b sem_prior --a decks/ogerpon_v9.csv --replicas 10
    "prior_antigo": {"PTCG_PRIOR_ANTIGO": "1"},
    "sem_prior": {"PTCG_W_PRIOR": "0"},

    # A parte NAO-LINEAR do prior: 100 arvores de profundidade 5, somadas a
    # logistica. Recupera 62% da vantagem do GBM (+0,99pp de +1,97 no top-1),
    # cabe em 103 KB e custa 0,14 ms por decisao de 2.000 disponiveis.
    # Os pesos NAO sao varridos: 1,0 e a soma direta dos dois scores, que e o
    # que o top-1 mediu.
    "arvores": {"PTCG_ARVORES": "1"},
    "arvores_meio": {"PTCG_ARVORES": "1", "PTCG_W_ARVORES": "0.5"},

    # ------------------------------------------------------------------
    # REMEDICOES — tudo aqui foi reprovado ANTES de 12/08, quando a busca
    # determinizava o NOSSO deck com uma lista que nao estava em jogo. Aquele
    # bug estragava justamente as simulacoes, que e onde estas variantes agem.
    # O prior mudou de +1,65pp para +10,11pp so por causa da correcao; nao ha
    # razao para supor que as outras nao mudaram tambem.
    # ------------------------------------------------------------------

    # 2 ply SOZINHO. Nunca foi medido isolado — a unica medicao (-4,9pp) veio
    # junto com o feixe. E as tres causas apontadas na epoca foram atacadas
    # desde entao: o turno dele era conduzido pela nossa L0 (hoje o rollout tem
    # o prior, que vale +10pp), com a mao dele preenchida pelo NOSSO deck (hoje
    # sorteia um arquetipo do meta) e o nosso deck errado (corrigido).
    "ply2": {"PTCG_PLY": "2"},
    "feixe4_novo": {"PTCG_FEIXE": "4"},
    "feixe8_novo": {"PTCG_FEIXE": "8"},

    # O peso do prior foi fixado em 10 quando ele valia +1,65pp. Agora que vale
    # +10,11pp, o peso otimo pode ser outro — mas os valores sao PRE-DEFINIDOS
    # por ordem de grandeza, nao varridos: a BASE_PRIORITY vai de 8 a 62 e os
    # logits do prior de -1,4 a +0,2. W=10 atravessa faixas; W=30 domina.
    "prior20": {"PTCG_W_PRIOR": "20"},
    "prior30": {"PTCG_W_PRIOR": "30"},

    # A DIVIDA mais antiga do projeto: o prior do meta na determinizacao do
    # adversario nunca passou pelo painel. Foi aceito contra regua unica
    # (+1,81pp) e esta em producao desde antes de o gate existir.
    "sem_meta_prior": {"PTCG_META_PRIOR": "0"},
}


def wilson(k, n, z=1.96):
    if not n:
        return float("nan"), float("nan"), float("nan")
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - m), min(1.0, c + m)


def rodar(variante, agente_b, deck_b, budget, n, replicas, jobs, deck_a):
    cmd = [sys.executable, str(RAIZ / "tools" / "arena_paralela.py"),
           "--a", "l1c", "--b", agente_b, "--n", str(n),
           "--replicas", str(replicas), "--jobs", str(jobs),
           "--budget", str(budget)]
    if deck_b:
        cmd += ["--deck-b", str(RAIZ / deck_b)]
    if deck_a:
        cmd += ["--deck-a", str(RAIZ / deck_a)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", **VARIANTES[variante])
    r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                       encoding="utf-8", cwd=str(RAIZ))
    import re
    m = re.search(r"AGREGADO\s+(\d+)/(\d+)", r.stdout)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variantes", default="rollout,feixe4")
    ap.add_argument("--n", type=int, default=900)
    ap.add_argument("--replicas", type=int, default=3)
    ap.add_argument("--jobs", type=int, default=6)
    ap.add_argument("--deck-a", default=None, help="o NOSSO deck; padrao sample")
    ap.add_argument("--casas", default="base",
                    choices=["base", "meta", "todas"],
                    help="base = o GATE (4 casas); meta = os arquetipos do "
                         "campo, EXPLORACAO SO (ganhamos de 93 a 99% delas, "
                         "porque nenhum agente disponivel pilota aquelas "
                         "listas); todas = as 8")
    # O resultado POR CASA so existia na tela. O `comparar_decks.py` chamava
    # este arquivo 20 vezes, cada uma medindo as quatro casas, e guardava so
    # o agregado — o gate conjuntivo (`nao regredir em nenhuma casa`) ficava
    # sem dado e exigia uma segunda rodada, mais curta e por isso cega.
    ap.add_argument("--json", default=None,
                    help="grava {variante: {casa: [vitorias, n]}} neste arquivo")
    args = ap.parse_args()

    global PAINEL
    PAINEL = {"base": PAINEL_BASE,
              "meta": PAINEL_META,
              "todas": PAINEL_BASE + PAINEL_META}[args.casas]
    if args.casas != "base":
        print("AVISO: as casas de meta NAO MEDEM MATCHUP, e isso esta MEDIDO\n"
              "       duas vezes. Trocar o `ref950` (IDs cravados) pelo `l1c`\n"
              "       nao resolveu: contra o Dragapult ganhamos 99,0% com o\n"
              "       l1c pilotando e 99,7% com a POLITICA NULA pilotando.\n"
              "       Todo o valor do nosso agente com deck alheio e 0,7 pp\n"
              "       sobre nao ter politica. Ver docs/meta-nao-mede-2026-08-23.md\n")

    variantes = [v.strip() for v in args.variantes.split(",")]
    for v in variantes:
        if v not in VARIANTES:
            raise SystemExit(f"variante desconhecida: {v} (tem: {', '.join(VARIANTES)})")

    print(f"painel | {len(PAINEL)} oponentes x {len(variantes)} variantes "
          f"| {args.replicas} replicas de {args.n}")
    print(f"nosso deck: {args.deck_a or 'sample'}\n")

    resultados: dict[str, dict[str, tuple]] = {v: {} for v in variantes}
    for rotulo, agente, deck_b, budget in PAINEL:
        print(f"-- {rotulo}", flush=True)
        for v in variantes:
            r = rodar(v, agente, deck_b, budget, args.n, args.replicas,
                      args.jobs, args.deck_a)
            if r is None:
                print(f"     {v:14} FALHOU")
                continue
            resultados[v][rotulo] = r
            p, lo, hi = wilson(*r)
            print(f"     {v:14} {100*p:5.1f}%  [{100*lo:.1f}; {100*hi:.1f}]",
                  flush=True)

    if args.json:
        pathlib.Path(args.json).write_text(
            json.dumps({v: {casa: list(par) for casa, par in casas.items()}
                        for v, casas in resultados.items()}),
            encoding="utf-8")

    print(f"\n{'='*74}\nAGREGADO DO PAINEL\n{'='*74}")
    print(f"  {'variante':14} " + " ".join(f"{r[:13]:>14}" for r, *_ in PAINEL)
          + f"{'TOTAL':>10}")
    base = variantes[0]
    for v in variantes:
        celulas = []
        tv = tn = 0
        for rotulo, *_ in PAINEL:
            r = resultados[v].get(rotulo)
            if not r:
                celulas.append(f"{'—':>14}")
                continue
            tv += r[0]
            tn += r[1]
            celulas.append(f"{100*r[0]/r[1]:13.1f}%")
        p, lo, hi = wilson(tv, tn)
        marca = "  <- base" if v == base else ""
        print(f"  {v:14} " + " ".join(celulas) + f"{100*p:9.1f}%{marca}")

    # a variante so passa se ganhar no total e nao regredir em nenhuma casa
    if len(variantes) > 1:
        print(f"\n  gate (contra `{base}`): ganhar no total e nao regredir em "
              f"nenhum oponente alem do IC")
        bv = sum(resultados[base].get(r, (0, 0))[0] for r, *_ in PAINEL)
        bn = sum(resultados[base].get(r, (0, 0))[1] for r, *_ in PAINEL)
        for v in variantes[1:]:
            tv = sum(resultados[v].get(r, (0, 0))[0] for r, *_ in PAINEL)
            tn = sum(resultados[v].get(r, (0, 0))[1] for r, *_ in PAINEL)
            if not (tn and bn):
                continue
            # Newcombe (1998) para a diferenca de proporcoes: combina os
            # intervalos de Wilson dos dois lados em vez do erro padrao de
            # Wald da diferenca, que perde cobertura perto de 0 e de 1.
            d, lo, hi = est.diferenca_de_proporcoes(tv, tn, bv, bn)
            # E o alfa corrigido para o numero de variantes testadas nesta
            # rodada. Testar nove hipoteses a 5% cada e esperar ~0,45
            # falso-positivo e chamar isso de descoberta.
            m = len(variantes) - 1
            _, lo_c, hi_c = est.diferenca_de_proporcoes(
                tv, tn, bv, bn, alfa=est.bonferroni(0.05, m))
            regrediu = []
            for rotulo, *_ in PAINEL:
                a, b = resultados[v].get(rotulo), resultados[base].get(rotulo)
                if not a or not b:
                    continue
                pa, la, _ = wilson(*a)
                pb, _, hb = wilson(*b)
                if la > 0 and pa < pb and _sobrepoe(a, b) is False:
                    regrediu.append(rotulo)
            veredito = "PASSA" if lo > 0 and not regrediu else "NAO PASSA"
            extra = ""
            if lo > 0 and lo_c <= 0:
                extra = "  (cai sob Bonferroni)"
            print(f"    {v:14} {100*d:+6.2f}pp  IC "
                  f"[{100*lo:+.2f}; {100*hi:+.2f}]  {veredito}{extra}"
                  + (f"  (regride em: {', '.join(regrediu)})" if regrediu else ""))
            if m > 1:
                print(f"    {'':14} {'':6}    Bonferroni({m}): "
                      f"[{100*lo_c:+.2f}; {100*hi_c:+.2f}]")


def _sobrepoe(a, b) -> bool:
    _, la, ha = wilson(*a)
    _, lb, hb = wilson(*b)
    return not (ha < lb or hb < la)


if __name__ == "__main__":
    main()
