> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T11 — no T10, foi a **ordem** ou a **magnitude**? **pré-registro**

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção no fim, **sem
> editar nada acima dela**.

---

## A pergunta que o T10 deixou aberta

O T10 adotou `FRACAO_ENERGIA_BANCO = 0.0` com **+0,88 pp** [+0,33; +1,43],
gate conjuntivo passando. Mas o documento registrou, no mesmo lugar:

> *"**`0,0` não é demonstradamente melhor que `0,5`.** O painel os separa por
> 0,23 pp, muito abaixo de qualquer resolução aqui. A escolha do `0,0` vem de
> ele ser o que foi medido com o instrumento certo — não de superioridade."*

Duas explicações continuam de pé, e elas levam a códigos diferentes:

| explicação | o que ela prevê |
|---|---|
| **magnitude** — o valor certo é perto de zero, e descontar pela metade desperdiça parte do ganho | `0,0` **vence** `0,5` por algo próximo de +0,3 pp |
| **ordem** — o que importa é a energia do ativo valer **mais** que a do banco; quanto mais, dá no mesmo | `0,0` e `0,5` **empatam** |

## Por que a pergunta vale uma rodada

**É o padrão do T6, e se ele se repetir vira regra e não coincidência.**

No T6, dois valores de compressão — um previsto e um **controle abaixo do
limiar** — renderam **+1,10** e **+1,03 pp**. O controle deveria render zero
pela hipótese registrada, e não rendeu: a explicação *"devolver autoridade ao
modelo"* foi **falsificada pelo próprio controle**, e o que sobrou foi a
**ordem** dos tipos na escada, não a distância.

Se aqui acontecer o mesmo, o relatório passa a ter **dois casos independentes**
do mesmo fenômeno: *o mecanismo estava certo na direção e errado na explicação*.
Isso é material de relatório, **não ganho de vitória** — e está declarado como
tal.

---

## O desenho

| | |
|---|---|
| protocolo | `comparar_decks.py --variante-a atual --variante-b p2_banco_meio --a decks/ogerpon_v9.csv --replicas 10 --n 1100` |
| `atual` | `FRACAO_ENERGIA_BANCO = 0.0` — **já é o adotado** |
| `p2_banco_meio` | `0.5` |
| família | **1 teste** |
| gate | **conjuntivo** — mas aqui o resultado esperado é empate, e empate **não muda nada**: o `0,0` já está embarcado |
| custo | ~3,3 h |

**O instrumento é o `comparar_decks`, não o painel** — armadilha nº 5.

---

## A previsão, registrada antes

> **Entre −0,4 e +0,5 pp, com o IC cruzando zero.**

**Fundamento:** os dois valores produzem a **mesma ordenação** em toda decisão
em que a comparação é "energia no ativo contra energia no banco" — que é o caso
que o T10 conserta. Eles só divergem quando a comparação envolve **quantidade**
de energia no banco contra outra coisa (recuo, promoção, proteger o substituto),
e essas decisões são minoria.

**Contra a previsão:** o painel deu 54,1% para o `meio` e 54,3% para o `zero` —
0,23 pp a favor do `zero`. Se a diferença real for essa, ela é **metade** da
resolução desta rodada, e o empate seria por falta de potência, não por
ausência de efeito. **Essa ambiguidade é inerente e está declarada.**

| observação | leitura |
|---|---|
| **empate com IC estreito** | é a **ordem**, não a magnitude — segundo caso do padrão do T6 |
| **`0,0` vence** | é a magnitude, e o valor certo é o extremo |
| **`0,5` vence** | zerar o banco cobra em recuo e promoção, e o `0,0` adotado está **errado** — reverter para `0,5` |

---

## Resultado — **EMPATE**, e a previsão acertou inteira

10 réplicas alternadas, 231 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` (banco = 0,0) | **54,64%** | ± 0,47 pp |
| `p2_banco_meio` (banco = 0,5) | **54,45%** | ± 0,70 pp |

| | |
|---|---|
| diferença | **+0,19 pp** a favor do `0,0` (erro padrão 0,27; Welch, 15,7 g.l.) |
| IC 95% | **[−0,37; +0,75]** — **cruza zero** |
| veredito | **empate estatístico. Não há vencedor.** |

**A previsão registrada era “entre −0,4 e +0,5 pp, com o IC cruzando zero”.**
Deu **+0,19 pp com o IC cruzando zero** — **as duas metades certas**. É a
primeira previsão do projeto que acerta ponto *e* veredito; no T10 eu acertei o
ponto e errei o veredito.

### Por casa, nada se move

| casa | `atual` | `meio` | A−B | IC 95% |
|---|---:|---:|---:|---|
| ref950+Lucario 0,05 s | 35,60% | 34,65% | +0,95 | [−0,35; +2,24] |
| ref950+Lucario 0,5 s | 35,26% | 35,52% | −0,25 | [−1,73; +1,22] |
| ref950+sample | 72,04% | 71,89% | +0,15 | [−1,03; +1,32] |
| primeira (piso) | 75,62% | 75,77% | −0,15 | [−1,46; +1,15] |

Conferência pós-hoc: pareando réplicas de mesmo índice, o `0,5` venceu **3 de
9** — moeda, exatamente o que se espera de um empate.

**Nenhuma casa separa os dois valores.** Se a magnitude importasse, o efeito
apareceria justamente nas casas de Lucario, que são onde o T10 rendeu — e lá o
sinal troca de direção entre as duas.

---

## A leitura, pela tabela escrita antes

> **empate com IC estreito** → é a **ordem**, não a magnitude — segundo caso do
> padrão do T6

**É a ordem.** O que o T10 conserta é a avaliação passar a enxergar que energia
no ativo e energia no banco **não são a mesma coisa**. *Quanto* menos vale a do
banco, dentro da faixa [0; 0,5], **não muda o resultado**.

### E a ambiguidade que eu declarei antes continua de pé

O painel separou os dois valores por **0,23 pp**. Esta rodada resolve **~0,58 pp**
(erro padrão 0,27 × 2,13). **Um efeito real de 0,23 pp seria invisível aqui** —
então o empate é compatível com “não há diferença” **e** com “há uma diferença
pequena demais para este instrumento”.

**O que muda na prática: nada.** O `0,0` já está embarcado, e nenhuma das duas
leituras recomenda trocá-lo.

### O paralelo com o T6, e ele é mais fraco do que parece

| | T6 | T11 |
|---|---|---|
| desenho | valor previsto + **controle abaixo do limiar** | dois valores que produzem a **mesma ordenação** |
| previsão | o controle deveria render **zero** | os dois deveriam **empatar** |
| resultado | o controle rendeu **+1,03**, igual ao previsto | empataram |
| natureza | **falsificação** — a explicação caiu | **confirmação** — a previsão se sustentou |

Os dois apontam para a **ordem** e não para a magnitude. Mas o T6 foi uma
**surpresa que derrubou a explicação**, e o T11 foi uma **previsão que se
confirmou**. Chamar os dois de “o mesmo padrão” é verdade sobre a conclusão e
exagero sobre a força: **um deles refutou algo, o outro não refutou nada.**

---

## ⚠ A comparação tentadora que **não** vale

O `atual` desta rodada marcou **54,64%**; na réplica do T10, o `atual` — que
então era `banco = 1,0` — marcou **53,54%**. A diferença de **+1,10 pp** bate
quase exatamente com o **+0,88 pp** que o T10 mediu.

**É proibido usar isso como confirmação.** Comparar duas sessões de medição
**entre si** é a **régua quebrada nº 4** deste projeto, catalogada porque já
inventou um número antes. As rodadas correram em horas diferentes, com carga de
máquina diferente, e nada nelas foi pareado.

Fica registrado como **coincidência agradável, não como evidência.**
