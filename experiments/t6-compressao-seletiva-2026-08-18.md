> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T6 — compressão seletiva de `ATTACK` e `END`: **pré-registro**

> **Categoria C** — bancada e medições. Alimenta o writeup da **Strategy**.
>
> ⚠ **ESTE DOCUMENTO FOI ESCRITO ANTES DE MEDIR.** Hipótese, direção esperada,
> N e critério de leitura estão fixados abaixo, como manda a Parte 1.1 do
> [`plano-mestre-strategy.md`](../legado/plano-mestre-strategy.md). O resultado entra
> depois, numa seção separada, **sem editar nada do que está acima dela**.
>
> Razão de ser rígido aqui: a busca em feixe pareceu +2,33 pp com p=0,022 e
> empatou exato quando o N dobrou. O critério escrito depois do número é o
> jardim de caminhos que se bifurcam.

---

## Por que este teste, e por que ele não é "a hipótese nº 13"

O plano-mestre o descreve como o último de uma fila, com a ressalva de que *"o
agente está num ótimo local testado por 20+ hipóteses"*. A
[`auditoria-do-plano-2026-08-18.md`](../legado/auditoria-do-plano-2026-08-18.md) o promove
a primeiro, por um motivo: **é a única hipótese restante com mecanismo medido de
ponta a ponta**, e não um palpite sobre onde o ganho pode estar.

### O que foi medido, e em que ordem

**1. Existe uma lacuna de comportamento, e ela é enorme.** Em 24.549 decisões de
jogadores com rating ≥ 1.003 ([`o-que-eles-fazem-2026-08-14.md`](../legado/o-que-eles-fazem-2026-08-14.md)),
comparando a escolha real deles com a que o **nosso ranking** faria na mesma
posição:

| quando eles jogam | nosso ranking escolhe outra coisa |
|---|---:|
| `END` | **100,0%** — 1.359 de 1.359 |
| `RETREAT` | 79,2% |
| `ABILITY` | 77,6% |
| **`ATTACK`** | **70,9%** |
| `ATTACH` | 54,6% |
| `CARD` / `NUMBER` / `YES` | **0,0%** |

Atacamos com **58%** da frequência deles e passamos o turno com **41%**.

**2. A causa não é falta de modelo.** O `0,0%` de `CARD`/`NUMBER`/`YES` fecha o
diagnóstico: **onde todas as opções têm o mesmo tipo, o prior decide sozinho e
acerta sempre.** O problema é a escala **entre** tipos.

    BASE_PRIORITY[PLAY]   = 55
    BASE_PRIORITY[ATTACK] = 12      43 pontos
    o prior move no máximo  ~17     (W_PRIOR=10 x logits de -1,5 a +0,2)

**Nenhum modelo atravessa isso.** Não é um problema de treino.

**3. A busca também não atravessa.** Medido em 14.926 decisões nossas
([`divergencia-com-busca-2026-08-15.md`](../legado/divergencia-com-busca-2026-08-15.md)),
as correções caem monotonicamente com a distância na escala:

| tipo | distância de `PLAY` | correções da busca |
|---|---:|---:|
| `ATTACH` | 5 | **867** |
| `ABILITY` | 9 | 644 |
| `END` | 47 | 58 |
| **`ATTACK`** | **43** | **23** |

**4. E o remédio óbvio já falhou — de um jeito que este teste explica.** A
compressão **uniforme** (`PTCG_COMPRESSAO`) deu **+2,03 pp** e encolheu para
**+0,91 pp** [−0,51; +2,32] ao replicar com 3× a amostra. Ela mexia nos
**quatro** tipos; a medição de 15/08 mostra que **só dois** precisavam. Os
outros dois a busca já corrigia — mexer neles foi ruído somado ao sinal.

---

## A intervenção

`main.py`: aproximar **apenas** `ATTACK` e `END` da âncora `ATTACH` (50), por
uma fração `S`. Nada mais muda.

```
novo = v + (50 - v) * S      só para OPT_ATTACK e OPT_END
```

### Os valores são pré-definidos por conta, não varridos

O prior move ~17 pontos. Para ter autoridade sobre `PLAY`(55) → `ATTACK`(12) =
43, o que sobrar precisa caber em 17 — ou seja **`ATTACK` ≥ 38**, que é
**S ≥ 0,68**.

| S | `ATTACK` | `END` | papel |
|---:|---:|---:|---|
| 0,00 | 12,0 | 8,0 | desligado (padrão) |
| **0,50** | **31,0** | 29,0 | **controle** — de propósito **abaixo** do limiar |
| **0,75** | **40,5** | 39,5 | o valor que a conta implica |

**O 0,50 não é um segundo palpite: é o controle do mecanismo.** Se ele mover o
resultado tanto quanto o 0,75, então o que age **não é** "devolver autoridade ao
prior", e a explicação está errada mesmo que o número seja bom.

### O que a variante NÃO preserva, e é deliberado

`ATTACK` e `END` passam a ficar **acima** de `CARD`(30), `RETREAT`(18) e
`DISCARD`(14). Preservar a ordem inteira é **incompatível** com dar autoridade ao
prior aqui: a afirmação da heurística — *"esgote tudo que não encerra o turno
antes de atacar"* — é exatamente a que a medição contradiz.

O que continua acima de `ATTACK` em S=0,75: `EVOLVE`(62), `PLAY`(55),
`ATTACH`(50), `ABILITY`(46), `ENERGY`(44), `ENERGY_CARD`(42). **O motor do deck
— anexar energia e usar a habilidade — continua vindo primeiro.** É o que
separa esta variante do erro que já custou caro: com `ATTACK` no **topo**, o
agente ganhava 24,7% [20,1; 29,8] do aleatório contra 82,3% [77,6; 86,2]
rebaixado.

`YES` e `NO` ficam em 12,0 de propósito — a divergência deles é **0,0%**.

---

## A previsão, registrada antes

> **S = 0,75: positivo, entre +0,5 e +2,0 pp.**
> **S = 0,50: indistinguível de zero.**

Fundamento da direção: a compressão uniforme, que diluía o efeito por quatro
tipos, já rendeu **+0,91 pp**; concentrar a mesma intervenção onde a busca
comprovadamente não corrige deveria render mais, não menos.

Fundamento do teto de +2,0: fechar a lacuna de frequência de ataque não é o
mesmo que fechar a lacuna de **força** — o professor imitado tem rating ~1.100
e joga outro deck, e o `top-1` contra imitação humana já se mostrou **proxy
fraco** cinco vezes.

**Contra a previsão pesa o histórico:** 20+ hipóteses medidas, ~4 sobreviveram, e
**a minha previsão de mesa errou no T1 cinco dias atrás** — registrei "neutro a
levemente negativo" para o Lively Stadium e ele rendeu +1,31 pp.

---

## N, poder e critério de leitura

| | |
|---|---|
| **protocolo** | `comparar_decks.py --variante-a atual --variante-b t6_ataque75`, **10 réplicas por lado**, n=1100 por casa |
| **por quê réplicas** | σ **não** cai com o tamanho da rodada ([`poder-da-bancada-2026-08-18.md`](../legado/poder-da-bancada-2026-08-18.md)); o agregado binomial do painel vem **39% estreito** pela sobredispersão de 1,39× |
| **sensibilidade** | **1,63 pp** com σ=1,30 (conservador; o T1 observou 0,58–0,67) |
| **família** | testes de política de escala — **2 testes** (S=0,75 e S=0,50), α=0,025 |
| **custo** | ~198 min por comparação |
| **gate** | **conjuntivo**: IC(Bonferroni 2) inteiro acima de zero **E** não regredir em nenhuma das 4 casas |

### Ordem de execução, e ela importa

**Rodar S=0,75 primeiro.** O controle S=0,50 só tem função **se o 0,75 passar** —
não faz sentido gastar 198 min controlando um efeito que não existe. Se o 0,75
não passar, o 0,50 não é rodado e isso fica registrado.

---

## O que falsifica o quê

| observação | o que ela derruba |
|---|---|
| 0,75 não passa no gate | a intervenção. O mecanismo pode continuar certo e a escala não ser a alavanca certa para ele |
| 0,75 passa **e** 0,50 passa igual | **a explicação**, não o resultado. Se estar abaixo do limiar do prior não muda nada, o ganho vem de outra coisa — e adotar sem entender é o que este projeto não faz |
| 0,75 passa no agregado e regride numa casa | o gate reprova. É o formato exato de "depender de matchup" que a rubrica 70.4 pergunta |
| ganho no `top-1` sem ganho no painel | nada de novo — é a **sexta** vez; `top-1` contra imitação é proxy fraco |

---

## Riscos declarados

1. **O agente está num ótimo local testado por 20+ hipóteses.** A base de acerto
   histórica é ~20%.
2. **Ataque prematuro.** `ATTACK` passa acima de `RETREAT`, e recuar antes de
   atacar às vezes é a jogada. O painel mede isso, mas só no agregado das quatro
   casas.
3. **A lacuna de frequência pode não ser um defeito.** O professor imitado tem
   rating ~1.100 e joga **outro deck**; o nosso ataca com 3 energias e escala
   sem teto, e atacar menos pode ser correto *para esta lista*. **A dívida do
   `letal` aponta na mesma direção**: o professor ataca menos quando pode
   nocautear, e uma das explicações não descartadas é que nocautear nem sempre é
   bom.
4. **Efeitos de ~1 pp ficam fora de alcance** e isso vai declarado, em vez de
   virar mais um "não passou".

---

## Reprodução

```bash
# o teste (198 min, desatendido)
python tools/comparar_decks.py --a decks/ogerpon_v6.csv \
    --variante-a atual --variante-b t6_ataque75 \
    --replicas 10 --n 1100 --familia 2

# o controle, SO se o de cima passar
python tools/comparar_decks.py --a decks/ogerpon_v6.csv \
    --variante-a atual --variante-b t6_ataque50 \
    --replicas 10 --n 1100 --familia 2
```

Código: `submission/main.py` (`PTCG_COMPRESSAO_ATAQUE`), variantes
`t6_ataque50` e `t6_ataque75` em `tools/painel.py`, e 12 testes em
`tests/test_compressao_ataque.py` que prendem os valores contra a conta.

---

## Resultado — **PASSOU**, e a previsão registrada acertou

10 réplicas por lado, 44.000 partidas cada, 218 minutos, sobre o deck **v7**:

| | vitórias | dispersão entre rodadas |
|---|---:|---:|
| `atual` | 51,93% | ± 0,67 pp |
| **`t6_ataque75`** | **53,03%** | ± 1,01 pp |

| correção | IC 95% | veredito |
|---|---|---|
| sem correção | **[+0,29; +1,91]** | não cruza zero |
| **Bonferroni(2)** — a família declarada | **[+0,15; +2,05]** | **não cruza zero** |

**+1,10 pp**, erro padrão 0,38 pp (Welch, 15,7 g.l.).

**A previsão registrada era +0,5 a +2,0 pp.** O resultado é **+1,10 pp** — dentro
da faixa. É a primeira previsão de mesa que acerta nesta semana, depois de errar
no T1, no acerto de carta e na identidade de carta.

### O gate por casa

| casa | `atual` | `t6_ataque75` | A−B | IC 95% |
|---|---:|---:|---:|---|
| ref950+Lucario 0,05s | 31,06% | 31,29% | −0,23 | [−1,54; +1,09] |
| ref950+Lucario 0,5s | 29,86% | 31,20% | −1,34 | [−2,79; +0,12] |
| **ref950+sample** | 71,41% | **73,45%** | **−2,04** | **[−3,07; −1,01]** |
| primeira (piso) | 75,38% | 76,13% | −0,75 | [−1,84; +0,35] |

**PASSA: vence no agregado e não regride em nenhuma das quatro casas.**

O ganho concentra-se em **ref950+sample** — o adversário de política forte com
baralho desencaixado, a única casa cujo IC exclui zero. Fica como observação,
não como achado: é uma casa de quatro.

### ⚠ O que isto ainda NÃO autoriza

**Não adotar ainda.** Duas exigências do protocolo, declaradas antes:

1. **o controle S=0,50** — está rodando. Se ele render o mesmo que o 0,75, a
   **explicação** cai (não o resultado): estar abaixo do limiar de alcance do
   prior deveria fazer diferença, e se não faz, o ganho vem de outra coisa;
2. **replicação** com configuração diferente, que a Parte 1.1 exige para
   qualquer efeito antes de adotar.

Adotar sem o controle seria aceitar o número sem entender o mecanismo — que é
exatamente o que este documento foi escrito para impedir.

### E um achado do mesmo dia que muda a leitura do porquê

O [`ordem-das-jogadas-2026-08-18.md`](../legado/ordem-das-jogadas-2026-08-18.md) mediu que
**46,3% dos turnos dos pilotos 1.000+ contêm dois ou mais ataques** (112 de 242,
com zero intervenção do adversário entre eles em 112 casos). Ou seja: a
justificativa que ancora `ATTACK` = 12 no código — *"atacar encerra o turno"* —
**não se sustenta como está escrita**.

Isso **não explica** o +1,10 pp, mas remove o argumento teórico que dizia que
subir o ataque deveria ser ruim. O valor certo de `ATTACK` volta a ser pergunta
empírica — e este teste é a primeira resposta dela.

## Controle S=0,50 — **passou IGUAL, e isso FALSIFICA a explicação**

10 réplicas por lado, 173 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 52,09% | ± 0,80 pp |
| **`t6_ataque50`** | **53,12%** | ± 0,69 pp |

**+1,03 pp**, IC 95% [+0,33; +1,73], **Bonferroni(2) [+0,21; +1,85]**.
**Gate por casa: PASSA.**

| | S = 0,75 | **S = 0,50 (controle)** |
|---|---:|---:|
| efeito | +1,10 pp | **+1,03 pp** |
| Bonferroni(2) | [+0,15; +2,05] | [+0,21; +1,85] |
| gate conjuntivo | PASSA | PASSA |

### O que isto derruba

A tabela de falsificação escrita **antes de medir** dizia:

> *0,75 passa **e** 0,50 passa igual → **a explicação**, não o resultado. Se
> estar abaixo do limiar do prior não muda nada, o ganho vem de outra coisa.*

**É exatamente o que aconteceu.** O 0,50 põe `ATTACK` em 31 — **24 pontos
abaixo** de `PLAY`(55), muito fora do alcance de ~17 do prior. Pela hipótese
registrada ele deveria render ~zero. Rendeu o mesmo que o 0,75.

**A explicação "devolver autoridade ao prior" está morta.**

### E o que sobra, medido

Comparando o que os dois valores mudam na **ordem** dos tipos:

| | `ATTACK` passa a superar | `END` passa a superar |
|---|---|---|
| **S = 0,50** | CARD, TOOL, SKILL, COND, NUMBER, RETREAT, DISCARD, YES, NO | TOOL, SKILL, COND, NUMBER, RETREAT, DISCARD, YES, NO |
| **S = 0,75** | *(os mesmos)* | *(os mesmos)* **+ CARD** |

**A única diferença de ordenação entre os dois é `END` ultrapassar `CARD`.** Todo
o resto é idêntico — e os efeitos também são.

> **O mecanismo real é o REORDENAMENTO DE TIPOS, não a distância.** O que paga é
> `ATTACK` e `END` passarem à frente de `CARD`, `RETREAT`, `DISCARD` e
> companhia. Quanto acima elas ficam é irrelevante dentro da resolução medida.

Isso é coerente com tudo o que 18/08 mediu sobre o prior: ele **é** a regra
posicional dentro do tipo ([`prior-contra-regra-trivial`](../legado/prior-contra-regra-trivial-2026-08-18.md)),
então dar-lhe "mais alcance" não podia mesmo ser a alavanca.

### E as duas rodadas são uma REPLICAÇÃO

O protocolo exige replicar todo efeito, com configuração diferente, antes de
adotar. Como os dois valores produzem essencialmente a mesma reordenação, as
duas execuções são duas medições independentes da **mesma intervenção**:

    +1,10 pp  e  +1,03 pp

Sete centésimos de ponto separando duas rodadas de 44.000 partidas cada. **A
exigência de replicação está cumprida.**

---

## Decisão: **adotado com S = 0,50**

O gate declarado passou **duas vezes**, com replicação, e o mecanismo — corrigido
— está entendido. Adotado.

**Por que 0,50 e não 0,75**, já que os números empatam: **parcimônia**. O 0,50
produz uma reordenação **menor** (mantém `END` abaixo de `CARD`) com o mesmo
efeito medido. Entre duas mudanças indistinguíveis, a que mexe menos numa escala
validada por dezenas de medições. **A escolha é por parcimônia, não por
evidência** — dentro da resolução da bancada os dois são o mesmo.

**É a terceira alteração aprovada do projeto**, depois do Tera Orb (+2,24 pp) e
do Lively Stadium (+1,04 pp) — e a **primeira que mexe na política**, não na
lista.
