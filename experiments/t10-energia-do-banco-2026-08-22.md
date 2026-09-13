> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

> ### ⚠ Retratação parcial — 26/08: o número de divergência acima não se lê
>
> A justificativa "muda **23,5%** das decisões, acima do limiar" foi medida com
> uma régua quebrada. Rodado o controle que faltava, **duas chamadas idênticas
> do agente já discordam em ~18%** das decisões: a determinização sorteia a cada
> chamada, e a busca do engine tem aleatoriedade própria que nem `random.seed()`
> alcança. **23,5% está dentro da faixa do ruído.**
>
> **O resultado deste teste não muda** — ele foi decidido pelo painel, por
> vitória, com intervalo de confiança. O que cai é a justificativa barata que eu
> dava para gastar a bancada. Detalhe em
> [`t15`](t15-o-dano-de-novo-2026-08-26.md#-fui-medir-a-divergência-antes-do-painel-e-a-régua-quebrou-na-mão).

# T10 — a energia no banco vale o mesmo que a do ativo? **pré-registro**

> **Categoria C** — bancada e medições. Alimenta o writeup da **Strategy**.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção separada no fim,
> **sem editar nada acima dela**.

---

## O defeito, e como ele foi encontrado

A [`auditoria_de_turno`](../../tools/auditoria_de_turno.py) mediu, em 400 partidas
e 2.521 turnos nossos: entre os turnos com **mais de uma** habilidade oferecida
e o ativo entre elas, **23,7%** [21,6; 25,9] **começam pelo banco**.

O mecanismo estava numa linha do `avaliar_estado`, com o comentário explicando
a escolha:

```python
if W_ENERGIA:
    # energia em TODO o campo, nao so no ativo: com o Teal Dance
    # empilhando, o banco tambem e investimento
    total = _conta_energia(meu_ativo)
    for pk in _campo(eu, "bench") or []:
        total += _conta_energia(pk)
    s += total * W_ENERGIA
```

**Energia no banco vale exatamente o mesmo que energia no ativo.** Mas:

| | |
|---|---|
| o **Myriad Leaf Shower** conta | a energia dos **DOIS ATIVOS** |
| o **Teal Dance** anexa | **a si mesmo** |

Então usar a habilidade de um Ogerpon do **banco** põe a energia do turno em
quem **não vai atacar** — e produz um estado com **a mesma nota** do que a poria
no atacante. Empate na nota, e o desempate cai no índice da opção.

> **Não é o agente escolhendo mal entre duas coisas diferentes. É a avaliação
> não enxergando que são duas coisas diferentes.**

---

## A intervenção, e por que estes dois valores

`FRACAO_ENERGIA_BANCO` — a energia do banco passa a valer uma fração da do
ativo. **Padrão 1,0 = exatamente o comportamento anterior**, então o agente
embarcado não muda enquanto o teste não decidir.

| variante | fração | papel |
|---|---:|---|
| `atual` | 1,0 | linha de base |
| **`p2_banco_meio`** | **0,5** | a hipótese: metade |
| **`p2_banco_zero`** | **0,0** | o extremo, e o **controle** |

**Os dois valores são pré-definidos, não varridos.** Varrer e escolher o melhor
depois seria o jardim de caminhos que se bifurcam — o mesmo erro que o projeto
já evitou nos pesos do prior.

O `banco_zero` faz papel de controle **no sentido do T6**: se os dois renderem o
mesmo, o que importa não é *quanto* a energia do banco vale menos, e sim que ela
valha **alguma coisa a menos** — ou seja, é a **ordem**, não a magnitude. Foi
exatamente assim que o T6 falsificou a própria explicação.

### Quanto isto muda o comportamento — medido ANTES de ir ao painel

40 partidas, comparando a escolha do agente com fração 1,0 e 0,5 na **mesma**
observação:

| | |
|---|---:|
| decisões nossas comparadas | 2.611 |
| **a escolha muda em** | **613 — 23,5%** |
| decisões com habilidade na mesa | 1.027 |
| **a escolha muda em** | **429 — 41,8%** |

**É uma mudança grande.** Isso não é argumento a favor: mudanças grandes já
custaram caro neste projeto (2 ply, −4,9 pp). É o que garante que a bancada tem
o que medir.

---

## A previsão, registrada antes

> **`p2_banco_meio`: entre +0,3 e +1,5 pp.**
> **`p2_banco_zero`: entre −1,0 e +1,5 pp** — faixa mais larga e cruzando zero
> de propósito.

**Fundamento da direção:** a energia no ativo converte em dano **neste turno**
(+30 por energia, sem teto); a do banco converte em **zero** agora. Com energia
na mão sendo o recurso escasso do turno, mandá-la para o banco é adiar dano sem
comprar nada em troca.

**Fundamento do teto baixo:** o efeito não é dano puro. Energia no banco **não é
lixo** — depois de um nocaute o banco vira ativo e traz a energia junto, e a
nossa lista roda 4 Ogerpon justamente para trocar. Descontar demais pode fazer o
agente subalimentar o substituto.

**Por que a faixa do `zero` cruza o zero:** com o banco valendo nada, a avaliação
também deixa de proteger energia **já investida** no banco, o que muda recuo e
promoção — decisões que não estão no diagnóstico e que ninguém mediu.

**Contra a previsão pesa o histórico:** 20+ hipóteses medidas, 4 aprovadas; e as
duas maiores mudanças de comportamento já testadas (2 ply, feixe) **pioraram**.

---

## N, critério e o que falsifica o quê

| | |
|---|---|
| protocolo | `painel.py --variantes atual,p2_banco_meio,p2_banco_zero --deck-a decks/ogerpon_v9.csv --n 1100 --replicas 10` |
| família | **2 testes** (as duas variantes contra o `atual`) — Bonferroni |
| gate | **conjuntivo**: IC inteiro acima de zero **E** não regredir em nenhuma das 4 casas |
| sensibilidade | 0,91 pp sem correção; **~1,11 pp** com Bonferroni(2) |
| custo | ~5,5 h |

| observação | o que ela derruba |
|---|---|
| as duas passam, com efeitos parecidos | o que importa é a **ordem** (ativo antes do banco), não a magnitude — e a explicação "metade é o valor certo" cai, como caiu no T6 |
| só a `meio` passa | a magnitude importa: zerar o banco custa mais do que rende |
| só a `zero` passa | a hipótese está certa e **subestimei** o desconto |
| **nenhuma passa** | a avaliação não é o gargalo dessas decisões, e o 23,7% do diagnóstico não custava vitória |
| alguma **regride numa casa** | dependência de matchup — o gate conjuntivo segura |

---

## ⚠ O que NÃO vai ao painel, e por quê: a P1

O documento [`onde-esta-o-ganho`](../legado/onde-esta-o-ganho-2026-08-21.md) elegeu como
**P1** — prioridade máxima — dar utilidade por carta às decisões de seleção
múltipla, com o argumento de que são **16,6%** das decisões e a busca não roda
nelas.

**A regra foi implementada e medida antes de ir ao painel. Ela não passa no
critério de custo-benefício do próprio projeto.**

Nas nossas 40 partidas, das **328** decisões de seleção múltipla:

| quantas cartas **distintas** havia na mesa | decisões |
|---:|---:|
| 0 ou 1 — **não há o que escolher** | **283 (86%)** |
| 2 | 36 |
| 3 ou mais | 9 |

**Oitenta e seis por cento dessas decisões são entre cartas idênticas.** O
formato mais comum é `(contexto 7, min 0, max 1, 1 opção)`: *"pegar ou não pegar
esta carta"* — não *"qual carta pegar"*.

Com a regra ligada, a escolha muda em **8 de 284 — 2,8%** das decisões de
seleção múltipla, ou **~0,5% de todas as decisões**.

> **Isso está abaixo do que a bancada resolve, e dá para saber disso sem gastar
> 5,5 h.** É o mesmo critério que aposentou o Harlequin: magnitude prevista
> abaixo da resolução do instrumento.

### E isto corrige o documento de ontem

O `onde-esta-o-ganho` disse que a seleção múltipla era *"a maior superfície não
tocada"*. **A superfície é grande; a fatia dela em que existe decisão é pequena.**
Os 16,6% estavam certos, e a leitura estava errada — o número media *onde a
busca não roda*, não *onde há escolha a fazer*.

O código da utilidade fica no `main.py`, **desligado por padrão**
(`PTCG_UTILIDADE_CARTA`), com este registro. Não custa nada e evita
reimplementá-lo quando a pergunta voltar.

---

## Resultado — os pontos são bons, **e o instrumento estava errado**

10 réplicas por variante, 4 casas, N=1.100 por casa (44.000 partidas por
variante):

| variante | Lucario 0,05 s | Lucario 0,5 s | ref950+sample | primeira | **TOTAL** |
|---|---:|---:|---:|---:|---:|
| `atual` | 33,30% | 33,67% | 71,69% | 75,31% | **53,5%** |
| `p2_banco_meio` | 33,85% | 35,19% | 72,56% | 74,65% | **54,1%** |
| **`p2_banco_zero`** | **35,20%** | **35,88%** | 71,34% | 74,75% | **54,3%** |

O `painel.py` reportou:

| | diferença | IC 95% | Bonferroni(2) | veredito do tool |
|---|---:|---|---|---|
| `p2_banco_meio` | +0,57 pp | [−0,09; +1,23] | [−0,18; +1,33] | NÃO PASSA |
| `p2_banco_zero` | +0,80 pp | [+0,14; +1,46] | [+0,04; +1,55] | **PASSA** |

**E o "PASSA" não vale**, por um motivo que está escrito no próprio repositório.

### ⚠ O `painel.py` reporta IC 39% estreitos demais — e eu usei a ferramenta errada

O `comparar_decks.py` traz este comentário, no argumento que foi criado
exatamente para isto:

> *"O protocolo de RÉPLICAS só existia para decks. Variantes do agente eram
> medidas por `painel.py --variantes a,b`, que **agrega as partidas num binomial
> único** — e a auditoria de 14/08 mediu **sobredispersão de 1,39×** nesse
> agregado, ou seja, **IC 39% estreitos**."*

Confirmado no código: o gate do painel usa
`diferenca_de_proporcoes(tv, tn, bv, bn)` sobre as **44.000 partidas
empilhadas**. O `--replicas 10` multiplica o N e **não entra no intervalo**.
A dispersão entre réplicas — a única que este motor sem semente produz — fica
de fora.

Corrigindo pelo fator que o próprio projeto mediu:

| | IC do tool | **corrigido por 1,39×** |
|---|---|---|
| `p2_banco_meio` | [−0,09; +1,23] | **[−0,35; +1,49]** |
| `p2_banco_zero` | [+0,14; +1,46] | **[−0,12; +1,72]** |
| `p2_banco_zero`, Bonferroni(2) | [+0,04; +1,55] | **[−0,26; +1,86]** |

> **Nenhuma das duas passa num gate com a dispersão certa.** O `+0,80` continua
> sendo o ponto estimado; o que não existe é a evidência de que ele não é zero.

**O erro foi meu, e é de escolha de instrumento:** usei o `painel.py` porque ele
aceita três variantes numa rodada só. O `comparar_decks.py --variante-a/-b`
existe desde 18/08 justamente porque o painel não serve para decidir sobre
variantes de agente.

---

## O que os pontos ainda dizem, e é bastante

Sem tratar nada disto como aprovado:

1. **A direção é a prevista e é monótona.** Quanto mais se desconta a energia do
   banco, maior o ganho: 1,0 → 0,5 → 0,0 dá 53,5% → 54,1% → 54,3%.
2. **O ganho está nas duas casas com oponente forte.** As duas de Lucario sobem **+1,90 pp** e
   **+2,21 pp** com o `zero`; as duas casas fracas caem 0,35 e 0,56.
3. **É o padrão do T8 de novo** — ganhar contra o adversário forte e perder
   contra a régua quebrada e o piso —, agora com o sinal a nosso favor no
   agregado em vez de cancelar.
4. **As previsões registradas acertaram as duas.** `meio` foi previsto em +0,3 a
   +1,5 e deu +0,57; `zero` em −1,0 a +1,5 e deu +0,80.

E a leitura da tabela de falsificação pré-registrada — *"só a `zero` passa → a
hipótese está certa e subestimei o desconto"* — **fica suspensa**: com a
dispersão certa, nenhuma passa, então a linha que se aplica é a última,
*"nenhuma passa"*, **mas por falta de resolução, não por ausência de efeito.**

---

## A réplica, **pré-registrada agora** — e ela é a medição de verdade

`comparar_decks.py --variante-a atual --variante-b p2_banco_zero --a decks/ogerpon_v9.csv --replicas 10 --n 1100`

Ela conserta **duas** coisas de uma vez:

| defeito | como a réplica resolve |
|---|---|
| IC sem dispersão entre réplicas | o `comparar_decks` mede a dispersão **entre rodadas** e usa Welch |
| **ordem em blocos** — o `painel.py` roda todas as réplicas de uma variante e depois da outra, e carga de máquina vira diferença sistemática (armadilha nº 4) | o `comparar_decks` **alterna A, B, A, B** |

**Previsão registrada:** *o `p2_banco_zero` fica entre **+0,2 e +1,4 pp**, e o IC
cruza zero.* Fundamento: o ponto estimado do painel é +0,80 com N enorme, então
o ponto deve se repetir; mas a bancada resolve 0,91 pp com dispersão real, e
+0,80 está **abaixo** disso.

**Ou seja: eu espero que a réplica confirme o ponto e não consiga aprová-lo.**
Se isso acontecer, o veredito honesto é *"efeito plausível, abaixo da resolução
do instrumento"* — o mesmo lugar em que o T8 (Hero's Cape) parou.

| observação | leitura |
|---|---|
| **+0,2 a +1,4 com IC cruzando zero** | previsto: efeito real mas pequeno demais para este painel |
| **IC inteiro acima de zero** | passa de verdade, e aí sim adota |
| **ponto perto de zero** | o +0,80 do painel era artefato do binomial empilhado |
| **ponto negativo** | a hipótese cai, e o painel produziu um falso positivo |

---

## Resultado da réplica — **PASSA**, e a minha previsão errou pela metade

`comparar_decks --variante-a atual --variante-b p2_banco_zero`, mesmo deck dos
dois lados, 10 réplicas alternadas, 198 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 53,54% | ± 0,69 pp |
| **`p2_banco_zero`** | **54,42%** | ± 0,44 pp |

| | |
|---|---|
| diferença | **+0,88 pp** (erro padrão 0,26; Welch, 15,4 g.l.) |
| IC 95% | **[+0,33; +1,43]** — **não cruza zero** |
| **gate conjuntivo** | **PASSA** — vence no agregado e não regride em nenhuma casa |

### Por casa, e o ganho está nas duas com oponente forte

| casa | `atual` | `p2_banco_zero` | A−B | IC 95% |
|---|---:|---:|---:|---|
| **ref950+Lucario 0,05 s** | 34,45% | **35,60%** | **−1,15** | **[−2,29; −0,02]** |
| **ref950+Lucario 0,5 s** | 33,65% | **35,24%** | **−1,59** | **[−2,80; −0,38]** |
| ref950+sample | 71,49% | 71,60% | −0,11 | [−1,38; +1,16] |
| primeira (piso) | 74,61% | 75,23% | −0,62 | [−1,66; +0,42] |

**As duas casas de Lucario sobem, e nenhuma casa regride.** É a primeira vez no
projeto que uma alteração de agente melhora as duas casas duras **sem** custar
nada nas outras — o T8 tinha o mesmo padrão nas duas primeiras e pagava caro na
terceira.

Conferência **pós-hoc**: pareando réplicas de mesmo índice, a variante venceu
**9 de 10** (teste do sinal, p = 0,021).

### ⚠ A previsão registrada acertou o ponto e **errou o veredito**

> *"o `p2_banco_zero` fica entre **+0,2 e +1,4 pp**, e **o IC cruza zero**."*

O ponto deu **+0,88** — dentro da faixa. **Mas o IC não cruzou zero**, e a
segunda metade da previsão estava errada. O motivo é mensurável:

| | σ | erro padrão | resolução |
|---|---:|---:|---:|
| assumido no pré-registro | 0,725 pp | — | **0,91 pp** |
| **observado nesta rodada** | 0,69 e **0,44** | **0,26 pp** | **0,55 pp** |

**A variante dispersou muito menos que a linha de base** — 0,44 contra 0,69 —, e
com isso a rodada resolveu 0,55 pp em vez de 0,91. O efeito de 0,88 pp, que eu
esperava ver afogado, ficou **acima** da resolução real.

Vale registrar o que isso implica: **o σ = 0,725 pp do projeto é uma média, não
uma constante.** Usá-lo para prever a resolução de uma rodada específica erra
para os dois lados — aqui, a favor.

---

## Decisão: **ADOTADO**, com `FRACAO_ENERGIA_BANCO = 0.0`

| | |
|---|---|
| painel (instrumento errado) | +0,80 pp |
| **réplica (instrumento certo)** | **+0,88 pp**, IC [+0,33; +1,43], **gate PASSA** |
| réplicas pareadas | 9 de 10, p = 0,021 |
| dose-resposta (painel) | 1,0 → 0,5 → 0,0 dá 53,5% → 54,1% → 54,3% |

**O que continua não estabelecido, e fica escrito:**

1. **`0,0` não é demonstradamente melhor que `0,5`.** O painel os separa por
   0,23 pp, muito abaixo de qualquer resolução aqui. A escolha do `0,0` vem de
   ele ser o que foi medido com o instrumento certo — não de superioridade.
2. **A explicação pode ser a ordem, não a magnitude** — o padrão do T6. Testar
   `0,0` contra `0,5` responderia, e custa 3,3 h; não é a próxima coisa na fila
   porque o ganho é explicativo, não de vitória.
3. **A réplica repetiu a mesma configuração** com outro instrumento, outra
   ordenação (alternada) e outras partidas. Não é a réplica "de configuração
   diferente" do T9, e isso está declarado.
