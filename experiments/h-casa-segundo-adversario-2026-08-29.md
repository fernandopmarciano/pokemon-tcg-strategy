> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entra numa seção no fim, sem editar nada
> acima.
>
> Índice: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# H-casa — existe um segundo adversário forte? **pré-registro**

> **Categoria C** — bancada. ⚠ **ESCRITO ANTES DE MEDIR.**

---

## O buraco que este teste tenta fechar

**Todo gate deste projeto foi julgado contra um arquétipo que hoje é 1,5%**
[1,0; 2,1] **do campo.** É a limitação mais séria do projeto e ela está declarada
no relatório. Duas tentativas de consertar já falharam, cada uma por um motivo
diferente e registrado:

| tentativa | por que falhou |
|---|---|
| `ref950` pilotando listas do meta | as heurísticas dele têm os **IDs do deck de Lucario cravados**; com outra lista vira parede |
| o **nosso** `l1c` pilotando listas do meta | está preso à **avaliação**, construída em cima do Ogerpon. Medido em 23/08: Dragapult pilotado pela política nula nos dá **99,7%**; pilotado pelo `l1c`, **99,0%**. Todo o valor do nosso agente com deck alheio é **0,7 pp** |

## Por que esta terceira tentativa é diferente

A causa da segunda falha é conhecida e específica: a avaliação carrega o plano do
Ogerpon (`W_ENERGIA` premia acúmulo, banco vale zero, não há termo para linha de
evolução). **A lista testada aqui roda quatro cópias de Teal Mask Ogerpon ex** e
usa a carta como atacante principal — é a lista modal do **Hydrapple ex**,
**17,9%** [16,3; 19,7] do campo, jogada exatamente assim por **170 dos 359**
pilotos do arquétipo (`decks/campo_hydrapple_ogerpon.csv`, de
[`campo-atual`](../campo-atual-2026-08-28.md)).

**É a única lista do campo cuja causa de falha conhecida não se aplica.**

## O desenho — quatro casas, e duas delas são controle

O nosso lado é sempre `l1c` + `decks/ogerpon_v9.csv`, exceto onde dito.

| | nosso lado | lado dele | o que isola |
|---|---|---|---|
| **A** | `l1c` + nossa | **`primeira`** + a deles | o teto: a lista deles sem política nenhuma |
| **B** | `l1c` + nossa | **`l1c`** + a deles | **o teste** |
| **C** | **`primeira`** + nossa | **`primeira`** + a deles | **controle de deck**: as duas listas sem política dos dois lados |
| **D** | `l1c` + nossa | `l1c` + **a nossa** | **controle do instrumento**: o espelho tem de dar ~50% |

**A quantidade que decide é Δ = A − B**, a queda na nossa vitória quando a
política assume o lado deles. É **exatamente** a forma da medição de 23/08, para
ser comparável: lá Δ = **0,7 pp**.

**N = 1.000 por réplica, 3 réplicas por casa.** ~2,5 min por mil partidas
medidos na sondagem, então ~35 min no total. IC de Wilson por casa; a diferença
entre casas usa erro padrão das proporções.

## As previsões, registradas antes

| casa | previsão |
|---|---|
| A | **93–97%** (a sondagem de 40 partidas deu 95,0% [83,5; 98,6]) |
| **B** | **60–90%** |
| C | **45–65%** |
| D | **47–53%** |

**E a previsão que importa: Δ ≥ 10 pp**, contra os 0,7 pp do Dragapult.
Fundamento: a avaliação sabe o que fazer com Ogerpon, e a lista deles é
Ogerpon com outro motor de energia.

**Contra a minha própria previsão:** eu já errei duas vezes ao supor que o `l1c`
generaliza — a tentativa de 23/08 tinha exatamente esse raciocínio ("o `l1c` não
tem carta nenhuma cravada, logo pilota qualquer lista") e o aviso de que não
funcionaria **já estava escrito acima dela**. A diferença aqui é o Ogerpon na
lista, e é só isso.

## A tabela de falsificação

| resultado de B | leitura | ação |
|---|---|---|
| **35% ≤ B ≤ 80%** | **existe casa nova** — a bancada deixa de ter um adversário só | **replicar** com configuração diferente antes de entrar no painel |
| 80% < B ≤ 95% | melhor que o Dragapult, mas ainda parede: pouca resolução para julgar variante | registrar, **não** adotar |
| **B > 95%** | **terceira falha da mesma família** | fechar a frente. O painel fica com um adversário só, e isso vira **propriedade medida**, não lacuna aberta |
| B < 35% | surpresa | **desconfiar do instrumento primeiro** — checar C e D antes de qualquer conclusão |

E os controles mandam mais que o teste:

- **se D sair fora de 45–55%**, a arena não está simétrica e **nada** das outras
  casas vale;
- **se C sair muito abaixo de 45%**, a lista deles é melhor que a nossa **sem
  política nenhuma** — e aí B mede deck, não piloto.

## O que este teste NÃO decide

Não decide trocar de lista: a Simulation fechou para submissões em 16/08.
Se B cair na faixa boa, o produto é **uma casa de bancada**, não uma mudança de
deck — e toda medição futura passa a poder ser julgada contra 17,9% do campo em
vez de 1,5%.

---

## Resultado — **o teste acertou a faixa, a previsão-chave errou, e o controle roubou a conclusão**

3.000 partidas por casa (3 réplicas de 1.000), 25 minutos no total.

| casa | o que é | resultado | previsão |
|---|---|---:|---|
| **A** | `l1c`(nossa) × `primeira`(deles) | **94,6%** [93,8; 95,4] | 93–97% ✅ |
| **B** | `l1c`(nossa) × **`l1c`(deles)** | **87,1%** [85,9; 88,3] | 60–90% ✅ |
| **C** | `primeira` × `primeira` | **89,2%** [88,0; 90,2] | 45–65% ❌ |
| **D** | espelho, nossa × nossa | **48,4%** [46,6; 50,2] | 47–53% ✅ |

### O instrumento está bom

**D = 48,4%**, indistinguível de 50% e batendo o espelho medido em 23/08 (49,5%
[47,8; 51,3]). A arena é simétrica; o resto das casas pode ser lido.

### Δ deu 7,5 pp — dez vezes o Dragapult, e ainda assim abaixo da previsão

| a política assumindo o lado dele | efeito |
|---|---:|
| **Dragapult** (23/08) — nula → `l1c` | 99,7% → 99,0% = **0,7 pp** |
| **Hydrapple+Ogerpon** (hoje) — nula → `l1c` | 94,6% → 87,1% = **7,5 pp** [+6,1; +8,9] |

**A hipótese central estava certa na direção:** a avaliação transfere muito mais
para uma lista que roda o nosso atacante do que para uma que não roda — **dez
vezes mais**. Mas a previsão registrada era **Δ ≥ 10 pp** e o intervalo inteiro
fica abaixo disso ([+6,1; +8,9]). **A previsão falhou**, e é a quarta vez em sete
que erro a magnitude acertando o sinal.

### ⚠ E o controle C derruba a leitura otimista inteira

**Com política nula dos DOIS lados, a nossa lista ganha 89,2%** [88,0; 90,2].

Isso quer dizer que **a maior parte da diferença entre as duas listas existe
antes de qualquer política entrar em campo**. A decomposição:

| de onde vem a nossa vitória | quanto |
|---|---:|
| **o deck, sem política nenhuma dos dois lados** (C) | **89,2%** |
| a nossa política, com o lado dele fixo em nulo (A − C) | **+5,5 pp** [+4,1; +6,8] |
| o que a política dele recupera (A − B) | **−7,5 pp** [−8,9; −6,1] |

**Não é o nosso agente que vence a lista deles: é a nossa lista que vence a
lista deles quando ninguém pilota direito.** A causa é conhecida e já estava
escrita no `painel.py` sobre as casas de meta: *"deck simples bem pilotado contra
deck complexo mal pilotado, que é verdade e é inútil"*. A lista do campo tem
**duas linhas de Estágio 2** (Applin→Dipplin→Hydrapple e Chikorita→Bayleef→
Meganium); a nossa tem um básico que ataca sozinho.

### Veredito: **não vira casa de bancada**

Pela tabela pré-registrada, **B = 87,1%** cai na faixa *"80% < B ≤ 95% →
melhor que o Dragapult, mas ainda parede: registrar, **não** adotar"*.

E há um motivo aritmético além da tabela: uma casa a **87%** tem pouca
resolução para julgar variante de agente. As mudanças que este projeto adota
valem de 0,59 a 1,09 pp; medi-las dentro de uma parede de 87% exigiria N muito
maior que o das casas atuais, para uma casa que **já se sabe** dominada por
diferença de deck.

**A frente do segundo adversário fecha, e agora com três causas medidas:**

| tentativa | por que falhou |
|---|---|
| `ref950` com lista alheia | IDs do Lucario cravados |
| `l1c` com Dragapult | a avaliação carrega o plano do Ogerpon — 0,7 pp |
| **`l1c` com a lista do campo que roda Ogerpon** | **a avaliação transfere (7,5 pp), mas o confronto é decidido pela complexidade da lista: 89,2% sem política nenhuma** |

**O painel fica com um adversário forte só, e isso deixa de ser lacuna em aberto
para ser propriedade medida três vezes.**

---

## O que este teste entregou, e não era o que ele foi buscar

**1. A decomposição que faltava para o relatório.** Pela primeira vez há um
número separando *deck* de *piloto* num confronto contra uma lista real do campo:
89,2% é deck, +5,5 pp é a nossa política, 7,5 pp é a política deles. Toda
tentativa anterior de medir "matchup" misturava os três.

**2. Uma virtude medida da nossa lista, e ela é argumento de Deck Score.**
A nossa lista **funciona sem piloto**: com política nula dos dois lados ela ganha
**89,2%** da lista modal do arquétipo que roda a mesma carta. Num campeonato de
agentes imperfeitos, robustez a piloto ruim é propriedade de projeto, não sorte —
e foi exatamente o critério declarado quando a lista foi escolhida (*"o nosso é
simples de propósito"*).

> **Ressalva, e ela é séria:** isto **não** diz que a nossa lista é melhor. Diz
> que ela é melhor **sob piloto nulo**, dentro desta arena. Os pilotos reais
> daquela lista têm rating ~1.000 na ladder e nós temos ~340. **A comparação sob
> piloto competente dos dois lados não existe e não pode ser feita aqui** — é a
> mesma limitação de sempre, e ela continua de pé.
