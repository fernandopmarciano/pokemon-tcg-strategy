> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.**
>
> Nasce do pedido do Fernando: *"avalie as informações de input do agente,
> acredito que algo está faltando."*

> ### ⚠ Retratação parcial — 26/08: o número de divergência acima não se lê
>
> A justificativa "muda **18,5%** das decisões, acima do limiar" foi medida com
> uma régua quebrada. Rodado o controle que faltava, **duas chamadas idênticas
> do agente já discordam em ~18%** das decisões: a determinização sorteia a cada
> chamada, e a busca do engine tem aleatoriedade própria que nem `random.seed()`
> alcança. **18,5% está dentro da faixa do ruído.**
>
> **O resultado deste teste não muda** — ele foi decidido pelo painel, por
> vitória, com intervalo de confiança. O que cai é a justificativa barata que eu
> dava para gastar a bancada. Detalhe em
> [`t15`](t15-o-dano-de-novo-2026-08-26.md#-fui-medir-a-divergência-antes-do-painel-e-a-régua-quebrou-na-mão).

# T14 — o que a avaliação não enxerga do outro lado da mesa

## A auditoria: o que o engine entrega × o que o agente lê

[`auditoria_de_entradas.py`](../../tools/auditoria_de_entradas.py) percorre
observações reais, conta cada campo, e cruza com onde ele aparece no
`submission/main.py`. **70 campos vêm preenchidos.**

O que o Fernando listou, conferido um a um:

| ele perguntou | resposta medida |
|---|---|
| Pokémon do campo | `active` e `bench` — **lidos, mas só os NOSSOS** na avaliação de estado |
| HP atual | `hp` e `maxHp` — **lidos** |
| energias em cada um | `energies` / `energyCards` — lidos **só no termo de ameaça** |
| os mesmos parâmetros para si | **lidos** |
| **custo de recuo** | **não existe na observação** — é dado de carta. Mas o engine **só oferece recuo legal**, então a viabilidade já está tratada, e a energia descartada aparece no termo de energia |
| cartas na mão | `handCount` lido; o **conteúdo** (`hand`) é lido na política por carta |
| prêmios de cada jogador | `prize` — **lido** |

**A intuição estava certa, e o buraco é mais específico do que "falta
informação":** o que falta é **o outro lado da mesa**.

## Quanto cada buraco pesa — 5.806 decisões nossas

| situação | ocorre em |
|---|---:|
| **banco dele NÃO vazio** | **93,6%** [92,9; 94,2] — média de **3,41** Pokémon |
| ativo dele com energia | 66,1% — média de 1,11 |
| algum dele chegou neste turno | 10,1% |
| **nosso banco cheio** | **0,0%** |
| **condições especiais** (veneno, queimadura, sono, paralisia) | **0,0%** |

**Dois campos saem da lista por medição, não por argumento:** `benchMax` e as
condições especiais nunca importam nestas partidas. Ignorá-los não custa nada.

---

## ⚠ A candidata A morreu antes do painel, e o motivo vale mais que o teste

**A ideia:** a energia no ativo **dele** deveria contar **a favor**. Não é
intuitivo e parecia mecânica pura — o Myriad Leaf Shower soma 30 por energia
anexada aos **dois** ativos, então a energia dele multiplica o **nosso** dano. É
o mesmo argumento que fez o projeto rejeitar o Crushing Hammer.

**Implementei, e ela muda 19,3% das decisões** — bem acima do limiar. Ia para o
painel.

**E está errada por construção.** A avaliação julga **estados**, e o estado que
ela pontua é o do **fim do turno** — depois do nosso ataque. Se o ataque
nocauteia, o ativo dele é substituído por um com **zero** energia:

| | efeito no score |
|---|---:|
| nocautear o ativo dele | **−17** pelo termo novo (1,11 × 15) |
| e | +300 do `W_KO`, mais o giro de prêmios |

O termo é pequeno perto do nocaute e **aponta na direção errada**: ele
**desestimula matar o alvo**, porque matar apaga a energia que ele estava
premiando.

> **O que é verdade é "atacar um alvo carregado causa mais dano" — e isso é uma
> propriedade da AÇÃO, não do ESTADO.** Uma avaliação de estado não consegue
> expressá-la sem premiar o alvo *continuar vivo*.

E isso explica, retroativamente, **por que premiar dano falhou duas vezes**
(−11,46 e −7,37 pp): a mesma confusão entre o valor de uma ação e o valor do
estado que ela deixa.

**Custo de matá-la aqui: zero. Custo de descobrir no painel: 3,6 h.**

---

## A candidata B, que vai ao painel

`PTCG_BANCO_DELE=1`: o banco **dele** conta contra, espelhando o nosso.

```python
s += len(nosso_banco) * W_BANCO        # ja existia
s -= len(banco_dele)  * W_BANCO        # novo
```

**Peso derivado, não escolhido:** o mesmo `W_BANCO` = 8 que já vale para o nosso
lado. Desenvolvimento é desenvolvimento — se o nosso vale 8, o dele vale −8.

**Por que é limpo, ao contrário da A:** o banco dele é uma propriedade do estado
que **não** é apagada pelo nosso ataque, e um adversário com banco montado é
pior para nós de forma inequívoca — ele repõe o atacante que derrubamos, e o
nosso deck ganha por prêmios.

| | |
|---|---:|
| ocorre em | **93,6%** das decisões |
| muda a escolha em | **18,5%** (T10 mudava 23,5% e passou; T13, 20,9%) |
| tamanho típico do termo | 3,41 × 8 ≈ **27 pontos** |

### A previsão, registrada antes

> **Entre −0,5 e +1,0 pp.**

**Fundamento do lado positivo:** é o maior buraco de informação que sobrou, ocorre
em 93,6% das decisões, e o peso não foi escolhido — é o espelho de um termo que
já existe.

**Fundamento do lado negativo:** o agente **não controla** o banco do adversário.
Um termo que ele não pode influenciar não muda a ordenação entre as opções
**exceto** quando o nosso ataque muda o campo dele — e isso é raro. Os 18,5% de
mudança podem ser ruído de desempate, não decisão informada.

**E esse é o mesmo argumento que matou a A.** A diferença: o banco dele **não é
apagado** pelo nosso ataque, então o termo não aponta para o lado errado — no
pior caso é inerte.

| observação | leitura |
|---|---|
| **IC acima de zero** | a cegueira sobre o outro lado custava; adotar após réplica |
| **empate** | o termo é inerte, como o argumento contrário previa. **Registrar e não adotar** |
| **negativo** | penalizar o banco dele desvia o agente de coisas que ele controla |

**Protocolo:** `comparar_decks.py --variante-a atual --variante-b t14b_banco_dele --a decks/ogerpon_v9.csv --replicas 20 --n 1100`. **20 réplicas desde o início** — o T13 ensinou que 10 não resolvem efeitos desta faixa. Família de 1. ~7,2 h.

---

## Sobre testar na ladder

**Não é possível.** As submissões da Simulation fecharam em 16/08 —
`submissions_disabled: True` na API. A última submissão do projeto é de 15/08 e
é a final. Detalhe em
[`simulation-fechou`](../simulation-fechou-2026-08-23.md).

Toda validação daqui em diante é de bancada, com a limitação já declarada: o
gate mede um arquétipo que é **3,1%** do campo.

---

## Resultado — **empate**, e um empate que ensina

20 réplicas alternadas, 404 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 55,14% | ± 0,68 pp |
| `t14b_banco_dele` | 55,24% | ± 0,54 pp |

| | |
|---|---|
| diferença | **+0,10 pp** (erro padrão **0,19**; Welch, 36,0 g.l.) |
| IC 95% | **[−0,30; +0,49]** |
| veredito | **empate estatístico** |

A previsão registrada era **−0,5 a +1,0 pp**. Deu **+0,10** — dentro da faixa.

### Este empate não é falta de potência

Com 20 réplicas a rodada resolveu **~0,40 pp**, e o efeito medido é **+0,10**.
**Dá para descartar qualquer coisa maior que ~0,5 pp** — é um nulo informativo,
não um "não sei".

Pela tabela pré-registrada: *"empate → o termo é inerte, como o argumento
contrário previa. **Registrar e não adotar**"*.

---

## As duas mortes do T14 dizem a mesma coisa

| | como morreu | por quê |
|---|---|---|
| **A** — energia do alvo | **por construção**, antes do painel | o termo **aponta para o lado errado**: nocautear apaga a energia que ele premiava |
| **B** — banco dele | **empate**, com o painel | o agente **não controla** o banco do adversário; o termo desloca todas as opções por quase o mesmo valor e não reordena nada |

> **A avaliação de estado só paga quando corrige algo que o agente CONTROLA.**

E o placar do projeto confirma, dos dois lados:

| adotado | o que o termo corrigia | efeito |
|---|---|---:|
| T6 | a ordem das **nossas** jogadas | +1,03 pp |
| T10 | onde a **nossa** energia cai | +0,88 pp |
| T13 | a rotação do **nosso** ativo | +0,59 pp |

| reprovado ou inerte | o que o termo descrevia | efeito |
|---|---|---:|
| premiar dano (absoluto) | estado **dele**, valor de uma **ação** | −11,46 pp |
| premiar dano (fração) | idem | −7,37 pp |
| T14a — energia do alvo | estado **dele** | morreu por construção |
| T14b — banco dele | estado **dele**, incontrolável | **+0,10 pp, inerte** |

**Três vitórias sobre o que controlamos; quatro nulos ou derrotas sobre o que
não controlamos.** Não é uma lei — são sete pontos — mas é a regularidade mais
forte que o projeto produziu, e ela **fecha a auditoria de entradas**: a
informação que falta na avaliação falta **por um motivo**.

---

## E isso deixa o déficit de ataque de pé

O agente ainda **ataca 2,5× menos** que pilotos fortes nas mesmas posições
(4,8% × 12,1%). O T13 mal moveu isso (0,39× → 0,43×), e o T14 não tocou.

**A causa está isolada:** o agente **não enxerga o dano que causa**. Os dois
termos que o mostrariam estão desligados —

```python
USAR_DANO_REAL   = os.environ.get("PTCG_DANO_REAL", "0") == "1"
USAR_DANO_FRACAO = os.environ.get("PTCG_DANO_FRACAO", "0") == "1"
```

— porque foram medidos em **−11,46 pp** e **−7,37 pp**.

**Mas essas medições são de um agente que não existe mais.** Elas foram feitas
antes do T6, do T10 e do T13, e o motivo registrado da falha foi *"premiar dano
empurra o agente a atacar cedo, e atacar encerra o turno"* — exatamente a
dimensão que o **T6 reequilibrou**.

**Uma medição vale para o estado em que foi feita.** Reabrir isto é o próximo
teste, e está pré-registrado em [`t15`](t15-o-dano-de-novo-2026-08-26.md).
