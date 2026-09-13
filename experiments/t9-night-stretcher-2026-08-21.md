> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T9 — Night Stretcher 3 → 1: **pré-registro**

> **Categoria C** — bancada e medições. Alimenta o writeup da **Strategy**.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção separada no fim,
> **sem editar nada acima dela**.

---

## A pergunta

O Night Stretcher é a **maior aposta do nosso deck contra o campo**, e nunca foi
medida:

| | |
|---|---|
| listas fortes que o jogam | **0 de 18** |
| nós | **3** |
| uso do nosso agente | **80%** dos turnos em que aparece (110 de 137) |

*"Coloque um Pokémon ou uma carta de Energia Básica do seu descarte na mão."*

**Zero de dezoito é a unanimidade mais forte que a tabela de consenso produz na
direção "só nossa"** — mais forte, inclusive, que os 16 de 16 da Hero's Cape na
direção oposta.

O uso de 80% do nosso agente vale pouco como evidência: ele usa **tudo** entre
50% e 100%, enquanto os pilotos fortes não passam de **59,4%** em nenhuma carta
([`treinadores-segurados`](../legado/treinadores-segurados-2026-08-19.md)).

---

## A intervenção, e por que estas cartas

`decks/ogerpon_v9.csv` — o v8 com **duas cartas de cada lado**:

| carta | v8 | **v9** | racional |
|---|---:|---:|---|
| Night Stretcher | 3 | **1** | a aposta em teste; o Fernando propôs manter 1 |
| Energy Search | 1 | **2** | déficit claro: **12 de 15** listas fortes jogam exatamente 2, e o nosso agente a usa em **93%** dos turnos |
| Basic {G} Energy | 19 | **20** | **a substituição direta** — a função principal do Stretcher para nós é recuperar Energia Básica do descarte; em vez de uma carta que busca energia no lixo, roda-se a energia |

### Por que duas cartas de cada lado, e não uma

Medido em três trocas de lista:

| troca | cartas mudadas | efeito | veredito |
|---|---:|---:|---|
| Tera Orb 2 → 4 | 2 | +2,24 pp | adotada |
| Gravity Mountain → Lively | 2 | +1,04 pp | adotada |
| Deluxe Bomb → Hero's Cape | **1** | +0,19 pp | **empate** |

Com σ = 0,725 pp e 10 réplicas a bancada resolve **0,91 pp**. As duas trocas que
passaram mexeram em **duas** cartas; a única de **uma** carta deu empate. **Três
pontos não são regra**, mas o desenho segue o que eles indicam.

### Consequência declarada, e ela é desconfortável

O v9 sobe de **23 para 24 energias**, e o campo joga **19**. **Isto aumenta a
nossa maior divergência não testada** em vez de reduzi-la.

É deliberado: a substituição direta do Stretcher é energia, e trocá-lo por outra
coisa mediria duas hipóteses ao mesmo tempo. **A divergência de energia é o teste
seguinte (T10), e este documento não a resolve.**

---

## A previsão, registrada antes

> **Entre +0,3 e +1,3 pp a favor do v9.**

**Fundamento da direção:** 0 de 18 é a unanimidade mais forte disponível, e o
campo é composto por gente que ganha 47,5% das partidas na ladder real contra
oponentes do nível dela.

**Fundamento do teto baixo, e do piso quase em zero:** o placar das divergências
já testadas está **2 a 1 a nosso favor** — acertamos no Tera Orb (+2,24) e no
Judge (o consenso nos custaria −2,36), e erramos no Lively (+1,04 para o campo).
O consenso não é autoridade, e o nosso deck difere do deles em energia e em
recursão de forma que pode justificar o Stretcher.

**E há um argumento mecânico contra a minha própria previsão:** rodamos **4
Ogerpon**, e o Stretcher recupera Pokémon do descarte. Num deck de atacante
único que entrega 2 prêmios por nocaute, recuperar o atacante pode valer mais
para nós do que para listas que jogam outra coisa.

**Contra a previsão pesa o histórico:** 20+ hipóteses, 3 aprovadas pelo gate; e a
minha previsão de mesa errou quatro vezes nesta semana e acertou duas.

---

## N, critério e o que falsifica o quê

| | |
|---|---|
| protocolo | `comparar_decks.py --a decks/ogerpon_v8.csv --b decks/ogerpon_v9.csv`, **10 réplicas por lado**, n=1100 |
| família | **1 teste** |
| gate | **conjuntivo**: IC inteiro acima de zero **E** não regredir em nenhuma das 4 casas |
| sensibilidade | **0,91 pp** com σ = 0,725 |
| custo | ~3,6 h |

| observação | o que ela derruba |
|---|---|
| o v9 passa no gate | os 2 Night Stretcher extras não pagavam, e o campo estava certo numa segunda divergência |
| empate com IC estreito | as duas listas são equivalentes na bancada; a aposta do Stretcher não custa nem paga |
| o v9 regride numa casa | dependência de matchup — a pergunta 70.4 |
| **o v8 ganha** | o Stretcher **paga** apesar de 0 de 18, e o placar contra o consenso vai a **3 a 1** |

---

## Resultado — **PASSOU no gate, e a previsão acertou**

10 réplicas por lado, 218 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `ogerpon_v8` | 52,38% | ± 0,79 pp |
| **`ogerpon_v9`** | **53,47%** | ± 0,91 pp |

| | |
|---|---|
| diferença | **+1,09 pp** a favor do v9 (erro padrão 0,38; Welch, 17,7 g.l.) |
| IC 95% | **[+0,29; +1,89]** |
| **gate conjuntivo** | **PASSA** — vence no agregado e não regride em nenhuma casa |

**A previsão registrada era +0,3 a +1,3 pp. O resultado é +1,09 pp** — dentro da
faixa. Segunda previsão certa da semana.

### O ganho está inteiro nas casas do deck real

| casa | v8 | v9 | A−B | IC 95% |
|---|---:|---:|---:|---|
| **ref950+Lucario 0,05 s** | 31,70% | **33,71%** | **−2,01** | **[−3,71; −0,31]** |
| **ref950+Lucario 0,5 s** | 32,05% | **34,05%** | **−1,99** | **[−3,64; −0,34]** |
| ref950+sample | 71,25% | 71,80% | −0,55 | [−1,41; +0,32] |
| primeira (piso) | 74,53% | 74,35% | +0,18 | [−0,95; +1,31] |

**As duas casas que pilotam um arquétipo real se movem ~2 pp cada, e as outras
duas não se movem.** É o padrão inverso do T8 (Hero's Cape), em que as casas se
cancelavam — aqui elas concordam, e são justamente as que se parecem com o campo.

**O campo estava certo:** zero de dezoito listas fortes jogam Night Stretcher, e
as duas cópias extras custavam.

---

## ⚠ NÃO ADOTADO AINDA — duas coisas faltam, e as duas foram declaradas antes

### 1. Replicação

A Parte 1.1 do plano-mestre exige **replicar todo efeito, com configuração
diferente, antes de adotar**. O T1 foi replicado; o T6 teve o controle fazendo
esse papel. O T9 tem **uma** medição.

### 2. Atribuição — mudei três cartas

| carta | v8 → v9 |
|---|---|
| Night Stretcher | 3 → 1 |
| Energy Search | 1 → 2 |
| Basic {G} Energy | 19 → 20 |

**O +1,09 pp pode vir de qualquer uma das três**, ou da combinação. O desenho de
duas cartas por lado foi escolhido para o efeito ser visível — e o preço é este.

---

## A replicação, **pré-registrada agora**

`decks/ogerpon_v9b.csv` — o **mesmo corte** do Night Stretcher, com
**preenchimento diferente**:

| carta | v8 | v9 | **v9b** |
|---|---:|---:|---:|
| Night Stretcher | 3 | **1** | **1** |
| Energy Search | 1 | 2 | **1** |
| Basic {G} Energy | 19 | 20 | **21** |

Ela responde **duas** perguntas com uma rodada:

| observação | leitura |
|---|---|
| **v9b também ganha ~1 pp** | o efeito é o **corte do Stretcher**, replicado com outra configuração. **Adotar** |
| **v9b não ganha** | o efeito era o **Energy Search**, e o corte do Stretcher é neutro. Adotar o v9, não o v9b, e registrar que a atribuição mudou de dono |
| ambos ganham, v9 > v9b | as duas coisas somam; o v9 fica |

**Previsão registrada:** *o v9b ganha, entre +0,5 e +1,5 pp.* Fundamento: as duas
casas que se moveram são as do deck real, e nelas o que muda é ter menos carta
morta na mão — não a busca por energia, que já estava em 93% de uso.

**Contra a previsão:** o Energy Search é a carta que o nosso agente mais usa
(93%), e 12 de 15 listas fortes jogam exatamente 2. Pode ser que a segunda cópia
seja o que pagou.

Protocolo idêntico: `--a decks/ogerpon_v8.csv --b decks/ogerpon_v9b.csv`,
10 réplicas, n=1100, gate conjuntivo.

---

## Resultado da réplica — **PASSOU, a previsão acertou, e o T9 é ADOTADO**

10 réplicas por lado, 216 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `ogerpon_v8` | 52,74% | ± 0,52 pp |
| **`ogerpon_v9b`** | **53,35%** | ± 0,51 pp |

| | |
|---|---|
| diferença | **+0,61 pp** a favor do v9b (erro padrão 0,23; Welch, 18,0 g.l.) |
| IC 95% | **[+0,13; +1,09]** |
| **gate conjuntivo** | **PASSA** — vence no agregado e não regride em nenhuma casa |

**A previsão registrada era +0,5 a +1,5 pp. O resultado é +0,61 pp** — dentro da
faixa. **Terceira previsão certa seguida.**

### O que isto resolve

A pergunta era de **atribuição**: o +1,09 pp do v9 vinha do corte do Night
Stretcher ou da segunda cópia de Energy Search? O v9b faz **o mesmo corte** com
**preenchimento diferente** — Energy Search fica em 1, e a vaga vai para Energia
Básica.

**O v9b ganha.** Pela tabela de leitura escrita antes de medir:

> *"**v9b também ganha ~1 pp** → o efeito é o **corte do Stretcher**, replicado
> com outra configuração. **Adotar**"*

**O efeito é do corte do Night Stretcher, e ele replicou em duas configurações
independentes.** O campo estava certo: zero de dezoito listas fortes o jogam.

### As casas, e a diferença de padrão em relação ao v9

| casa | v8 | v9b | A−B | IC 95% |
|---|---:|---:|---:|---|
| ref950+Lucario 0,05 s | 33,25% | 33,39% | −0,14 | [−0,98; +0,71] |
| ref950+Lucario 0,5 s | 32,15% | 33,16% | −1,01 | [−2,28; +0,26] |
| ref950+sample | 70,65% | 71,51% | −0,85 | [−2,37; +0,67] |
| primeira (piso) | 74,93% | 75,31% | −0,38 | [−1,77; +1,01] |

**Ganha nas quatro, e em nenhuma isoladamente.** É o oposto do v9, em que duas
casas carregavam ~2 pp cada e as outras duas não se moviam. Com N por casa, é
esperado que o agregado resolva o que as casas não resolvem — mas **registra-se
que os dois padrões são diferentes**, e nada aqui explica por quê.

### Uma conferência de robustez, declarada como **pós-hoc**

As réplicas alternam A, B, A, B, então réplicas de mesmo índice rodam juntas na
máquina. Comparando-as par a par:

| rodada | o corte venceu | teste do sinal |
|---|---:|---:|
| T9 (`v9`) | **8 de 10** | p = 0,109 |
| T9b (`v9b`) | **9 de 10** | **p = 0,021** |
| **as duas juntas** | **17 de 20** | — |

**Isto não estava pré-registrado**, e por isso não decide nada — entra como
conferência de que o ganho não vem de duas ou três réplicas extremas.

---

## Decisão: **adotado o `ogerpon_v9`**, e por quê ele e não o v9b

| | efeito contra o v8 | IC 95% |
|---|---:|---|
| **`ogerpon_v9`** | **+1,09 pp** | [+0,29; +1,89] |
| `ogerpon_v9b` | +0,61 pp | [+0,13; +1,09] |

A regra estava escrita antes: *"ambos ganham, v9 > v9b → as duas coisas somam;
o v9 fica"*.

> ⚠ **E o v9 > v9b NÃO está estabelecido.** A diferença entre os dois é de
> **0,48 pp**, abaixo dos **0,91 pp** que a bancada resolve, e os IC se
> sobrepõem quase inteiros. **Os dois são indistinguíveis no instrumento.** O v9
> entra pela regra pré-registrada e pelo ponto estimado maior, não por
> superioridade demonstrada.

**O que o v9 muda no deck embarcado:**

| carta | v8 → **v9** |
|---|---|
| Night Stretcher | 3 → **1** |
| Energy Search | 1 → **2** |
| Basic {G} Energy | 19 → **20** |

### A consequência declarada em 21/08 continua de pé

O v9 sobe para **24 energias** contra as 19–20 do campo, **aumentando** a nossa
maior divergência não testada. Foi declarado antes de medir e continua valendo.

**E o v9b traz um dado novo sobre isso:** ele roda **25** energias — duas a mais
que o v8 — e mesmo assim ganha. **Excesso de energia, na faixa 23–25, não
destruiu o ganho.** Não é um teste da divergência de energia, e não substitui
um; é o que se pode dizer com o que foi medido.

### Placar contra o consenso do campo, atualizado

| divergência testada | quem estava certo |
|---|---|
| Tera Orb 2 → 4 | **nós** (+2,24 pp) |
| Judge 1 → 4 | **nós** (o consenso custaria −2,36 pp) |
| Gravity Mountain → Lively | **o campo** (+1,04 pp) |
| **Night Stretcher 3 → 1** | **o campo** (+1,09 / +0,61 pp, replicado) |

**2 a 2.** O consenso não é autoridade nem ruído: acerta metade das vezes, e a
única forma de saber qual metade é medir cada uma.
