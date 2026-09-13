> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T8 — Hero's Cape contra Deluxe Bomb, com poder: **pré-registro**

> **Categoria C** — bancada e medições. Alimenta o writeup da **Strategy**.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção separada no fim,
> **sem editar nada acima dela**.

---

## Por que reabrir uma pergunta já testada

Esta comparação **já foi feita** em 14/08
([`cape-vs-bomba-2026-08-14.md`](../legado/cape-vs-bomba-2026-08-14.md)) e deu:

> **+0,36 pp** a favor da bomba, IC 95% **[−1,91; +2,63]**

**Um intervalo de 4,5 pp de largura.** Ele não separa +2 de −2, muito menos o
~1 pp em que os efeitos deste jogo vivem. Aquele "empate" significava
**"não sei"**, e o projeto o registrou como decisão.

**O que mudou em 19/08:** o σ da bancada foi estimado direito
([`sigma-bem-estimado`](../legado/sigma-bem-estimado-2026-08-19.md)) — **0,725 pp**,
IC [0,57; 0,99], de 30 rodadas e 27 g.l., contra o 1,30 pp que vinha de
estimativas com 4–6 g.l. Com 10 réplicas por lado a bancada enxerga **0,91 pp**.

**O intervalo fica cerca de cinco vezes mais estreito que o do teste original.**
A pergunta passa a ser respondível.

## E o consenso é unânime, agora com 16 listas

Refeito contra o **v7** e com o campo atualizado:

| carta | em quantas listas fortes | mediana | faixa | **nossa** |
|---|---|---:|---|---:|
| **Hero's Cape** | **16 de 16** | **1** | **1–1** | **0** |
| Deluxe Bomb | **0 de 16** | 0 | — | **1** |

**Dezesseis de dezesseis jogam exatamente uma Hero's Cape. Nenhuma joga a
Deluxe Bomb.** É a divergência mais forte que a tabela de consenso pode
produzir, e ela é **binária**: as duas são ACE SPEC, e o engine aceita **uma por
deck**.

## E há um mecanismo medido, não só consenso

Do documento de 14/08, contra os 16 baralhos do campo:

| | decks que nos derrubam de um golpe |
|---|---:|
| **sem** a capa | **6 de 16** — 37,5% [18,5; 61,4] |
| **com** a capa | **0 de 16** — 0,0% [0,0; 19,4] |

A capa dá +50 PS ao Pokémon que a segura. O Ogerpon tem 210; com a capa, 260 —
e isso o tira do alcance de um golpe de seis arquétipos do campo.

**Consenso unânime + mecanismo medido + teste anterior sem poder.** É a melhor
combinação disponível para gastar 3,6 h de painel.

---

## A intervenção

`decks/ogerpon_v8_cape.csv` — o **v7 com uma única troca**:

    Deluxe Bomb (1167)  ->  Hero's Cape (1159)

Verificado: 60 cartas, `diff` contra o v7 mostra **uma linha**, o engine aceita a
lista, e continua havendo exatamente **1 ACE SPEC**.

---

## A previsão, registrada antes

> **Entre 0 e +1,5 pp a favor da capa.**

**Fundamento da direção:** o mecanismo é real e grande — sair do alcance de um
golpe de 37,5% do campo muda partidas. E 16 de 16 pilotos fortes concordam,
o que já se mostrou informativo: das três divergências testadas até agora, o
campo estava certo em uma (o Lively, +1,04 pp) e errado em duas.

**Fundamento do teto:** o painel **não é o campo**. Ele roda quatro adversários
fixos, e a medição dos "6 de 16 derrubam de um golpe" é sobre os **arquétipos do
meta**, não sobre as casas do painel. O próprio documento de 14/08 registra que
o evento é raro o bastante para não aparecer em 800 partidas por casa. **Pode ser
que o painel simplesmente não contenha a situação em que a capa paga.**

**Contra a previsão pesa o histórico:** 20+ hipóteses, 3 sobreviventes; e a minha
previsão de mesa errou três vezes nesta semana e acertou duas.

---

## N, critério e o que falsifica o quê

| | |
|---|---|
| protocolo | `comparar_decks.py --a decks/ogerpon_v7.csv --b decks/ogerpon_v8_cape.csv`, **10 réplicas por lado**, n=1100 |
| família | **1 teste** — não há segunda variante; a escolha é binária |
| gate | **conjuntivo**: IC inteiro acima de zero **E** não regredir em nenhuma das 4 casas |
| sensibilidade | **0,91 pp** com σ=0,725 |
| custo | ~3,6 h |

| observação | o que ela derrubaria |
|---|---|
| a capa passa no gate | a Deluxe Bomb sai, e o placar contra o consenso vai a 2–2 |
| empate com IC estreito | **desta vez "empate" significa empate**, não "não sei" — e vira evidência de que o painel não contém a situação da capa |
| a capa regride numa casa | dependência de matchup, que é a pergunta 70.4 |
| a bomba ganha | o campo está errado numa quarta divergência, e é o resultado mais surpreendente possível |

**A diferença entre este teste e o de 14/08 não é a hipótese — é o poder.** Se
der empate de novo, o intervalo estreito torna esse empate um resultado, e não
uma lacuna.

---

## Resultado — **empate no agregado, e duas casas em DIREÇÕES OPOSTAS**

10 réplicas por lado, 218 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `ogerpon_v7` (Deluxe Bomb) | 52,69% | ± 0,71 pp |
| `ogerpon_v8_cape` (Hero's Cape) | 52,50% | ± 0,62 pp |

| | |
|---|---|
| diferença | **+0,19 pp** a favor da bomba (erro padrão 0,30) |
| IC 95% | **[−0,44; +0,82]** |
| veredito | **empate estatístico** |

**E desta vez o empate é um resultado.** O intervalo tem 1,3 pp de largura contra
os 4,5 pp de 14/08 — ele **exclui** qualquer efeito maior que ~0,8 pp em
qualquer direção. A pergunta que o teste original deixou em aberto está fechada:
**no agregado do painel, a troca não vale nada.**

**A previsão registrada era "entre 0 e +1,5 pp a favor da capa".** O ponto
estimado caiu do outro lado do zero (−0,19 pp para a capa). Errei a direção, e o
intervalo mal alcança a faixa que previ.

---

## O achado que não estava previsto: a carta é dependente de matchup, e isso foi medido

| casa | v7 (bomba) | v8 (capa) | A−B | IC 95% |
|---|---:|---:|---:|---|
| **ref950+Lucario 0,05 s** | 30,68% | **32,86%** | **−2,18** | **[−3,33; −1,03]** |
| ref950+Lucario 0,5 s | 31,05% | 31,54% | −0,48 | [−1,77; +0,80] |
| **ref950+sample** | **73,15%** | 70,99% | **+2,15** | **[+0,55; +3,76]** |
| primeira (piso) | 75,91% | 74,64% | +1,27 | [−0,01; +2,55] |

**Duas casas se separam, em direções opostas, com efeitos de tamanho quase
idêntico** — e é por isso que o agregado dá zero. Elas se cancelam.

É a **primeira vez** que um teste deste projeto produz efeitos significativos em
sentidos contrários entre casas. O gate conjuntivo existe para pegar exatamente
isto, e aqui ele nem precisou opinar: o agregado já não apontou vencedor.

### E as duas casas não são equivalentes

| casa | o que ela é |
|---|---|
| `ref950+Lucario` | política forte pilotando **um arquétipo real do campo** |
| `ref950+sample` | política forte pilotando **o baralho do exemplo oficial**, que ninguém joga |

**A capa ganha contra o deck real e perde contra o deck que ninguém joga.**

Isso é consistente com o consenso: as 16 listas fortes jogam a capa porque
enfrentam **o campo**, e no campo 6 de 16 arquétipos derrubam o Ogerpon de um
golpe sem ela. O `ref950+sample` não é o campo.

> **A leitura honesta, e ela é sobre a bancada, não sobre a carta:** o painel
> **não consegue arbitrar** esta escolha, porque metade dele mede uma situação
> que a ladder não contém. Antes isso era suspeita; agora é medição.

---

## ⚠ ADOTADA EM 20/08 — por decisão do Fernando, **contra o gate declarado**

O gate diz não, e continua dizendo. A capa entrou como `decks/ogerpon_v8.csv`
por **decisão explícita**, tomada depois de ler este documento inteiro. Fica
registrado como o que é: **a primeira alteração do projeto adotada sem passar no
critério de aceitação.**

O argumento a favor, e ele não é fraco:

| | |
|---|---|
| consenso | **16 de 16** listas fortes jogam exatamente 1 Hero's Cape; **0 de 16** jogam a Deluxe Bomb |
| mecanismo | +50 PS tiram o Ogerpon do alcance de um golpe de **6 dos 16** arquétipos do campo |
| bancada | **empate**, com IC estreito — ela não vê diferença, em nenhuma direção |

### E o argumento que NÃO vale, porque foi testado

A leitura tentadora era: *"a casa que decidiu contra a capa é a régua quebrada
nº 2 do próprio projeto; sem ela a capa passaria"*. **Medido, e é falso.**

| teste | com as 4 casas | **sem** `ref950+sample` | virou? |
|---|---|---|---|
| T1 Lively | −1,06 [−1,59; −0,53] | −1,34 [−2,00; −0,68] | não |
| T6 compressão 0,75 | −1,09 [−1,67; −0,51] | −0,77 [−1,47; −0,07] | não |
| T6 compressão 0,50 | −1,02 [−1,68; −0,37] | −1,08 [−1,81; −0,35] | não |
| T7 attach | −0,08 [−0,78; +0,61] | −0,12 [−0,96; +0,71] | não |
| **T8 Hero's Cape** | **+0,19 [−0,44; +0,82]** | **−0,46 [−1,13; +0,20]** | **não** |

Sem a casa suspeita a capa passa de levemente atrás para levemente à frente —
**e o intervalo continua cruzando zero**. Ela **não passaria no gate nem assim**.

> **A adoção se apoia em evidência EXTERNA — consenso do campo e mecanismo —,
> não numa bancada defeituosa.** A bancada foi consultada, respondeu "não vejo
> diferença", e a decisão foi tomada apesar disso. É uma coisa legítima de se
> fazer; é outra coisa fingir que a bancada concordou.

### O que isto obriga no writeup

O relatório **não pode** listar a capa entre as alterações aprovadas pelo
critério. São **três** aprovadas pelo gate (Tera Orb, Lively, compressão) e
**uma** adotada por julgamento contra ele. A distinção entra no texto.

---

## O registro do que o gate dizia

*(mantido como escrito antes da decisão)*

## A decisão do gate: **não adotada**

O gate declarado exige vencer no agregado. Não venceu. **A Deluxe Bomb fica.**

Registro do desconforto, porque ele é real: há um argumento para adotar a capa
mesmo assim — 16 de 16 pilotos fortes a jogam, o mecanismo está medido, e a casa
em que ela ganha é a que se parece com o campo. **Não adotei**, e o motivo é o
que este projeto inteiro defende: escolher a casa que confirma a hipótese
**depois** de ver o resultado é o jardim de caminhos que se bifurcam. O gate foi
declarado antes; ele diz não.

**O que muda é outra coisa:** esta medição vira evidência direta para a pergunta
**70.4** da rubrica — *"quão bem a estratégia evita depender de matchups
específicos?"*. Temos agora uma carta com **+2,2 pp num matchup e −2,2 pp em
outro**, medidos com IC que não cruzam zero. É o formato exato da pergunta, com
número.

---

## O que fica em aberto

| # | pergunta | como responder |
|---|---|---|
| **A** | a capa paga **contra o campo real**, e o painel é que não a enxerga? | exigiria casas de meta que funcionem como gate — e elas [não funcionam](../legado/consenso-listas-fortes-2026-08-14.md): ganhamos de 93 a 99% delas porque nenhum agente pilota aquelas listas |
| **B** | o `ref950+sample` deveria continuar no gate? | ele é 1 de 4 casas e move o agregado; mas tirá-lo depois de ver este resultado seria escolher a régua pelo número |

**A pergunta B fica registrada e não resolvida nesta sessão.** Mexer na
composição do painel logo após um teste em que ele decidiu contra a hipótese é
exatamente o que não se faz.
