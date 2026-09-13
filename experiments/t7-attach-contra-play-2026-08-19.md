> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T7 — `ATTACH` contra `PLAY`: **pré-registro**

> **Categoria C** — bancada e medições. Alimenta o writeup da **Strategy**.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** Hipótese, valores, N e critério fixados abaixo.
> O resultado entra numa seção separada no fim, **sem editar nada acima dela**.

---

## De onde vem

Três medições de 18–19/08 apontam para a mesma fronteira:

**1. Perdemos metade das decisões de anexar energia.** Contra pilotos com rating
≥ 1.000 **do nosso próprio arquétipo**, 3.304 decisões
([`decisoes-ogerpon-forte`](../legado/decisoes-ogerpon-forte-2026-08-18.md)):

| quando eles fazem | escolhemos outra coisa |
|---|---:|
| `ATTACH` | **52,4%** (188 de 359) |

**2. E o concorrente é `PLAY`, não outra coisa.** Detalhando as 359 decisões:

| eles anexam energia, e nós… | casos | % |
|---|---:|---:|
| escolhemos **outro tipo de jogada** | 188 | **52,4%** |
| anexamos, e no **mesmo destino** | 171 | 47,6% |

**Quando decidimos anexar, concordamos com o destino em 100% dos casos.** O erro
é inteiramente *não decidir anexar* — e a causa é a escada: `PLAY` = 55 contra
`ATTACH` = 50. Havendo carta para jogar, jogamos a carta.

**3. Os pilotos fortes NÃO ordenam essas duas.** Na medição de posição dentro do
turno ([`ordem-das-jogadas`](../legado/ordem-das-jogadas-2026-08-18.md)), 421 turnos:

| jogada | p25 | mediana | p75 |
|---|---:|---:|---:|
| `PLAY` | 0,14 | **0,38** | 0,62 |
| `ATTACH` | 0,14 | **0,38** | 0,62 |

**Idênticas.** Eles intercalam as duas conforme a posição pede; não há
precedência.

## E o T6 diz qual é a alavanca

O [`T6`](t6-compressao-seletiva-2026-08-18.md) mediu que o que paga é a **ordem**
dos tipos, não a distância — o controle abaixo do limiar do prior rendeu o mesmo
que o valor acima dele. Se `ATTACH` perde para `PLAY` por ser 5 pontos menor, a
intervenção é mexer nessa relação, e só nela.

---

## A intervenção

Um parâmetro novo, `PTCG_PRIO_ATTACH`, com o mesmo desenho do `PTCG_PRIO_ABILITY`
que já existe. Nada mais muda.

| variante | `ATTACH` | relação com `PLAY` (55) | por quê |
|---|---:|---|---|
| atual | 50,0 | abaixo | `PLAY` sempre ganha |
| **T7a — empata** | **55,0** | **igual** | o desempate cai para a posição, e a posição é o que os pilotos fortes acertam ~62% das vezes nas decisões de tipo único |
| **T7b — acima** | **57,0** | acima | `ATTACH` sempre ganha |

**A T7a é a primária**, porque é a que corresponde ao observado: eles não
ordenam, intercalam. A T7b existe para responder *"a direção importa, ou só
importa deixar de ser sempre `PLAY`?"*.

**Valores pré-definidos, não varridos:** 55,0 é o valor exato de `PLAY`; 57,0 é o
ponto médio entre `PLAY` (55) e `EVOLVE` (62). Nenhum dos dois foi escolhido
olhando resultado.

---

## A previsão, registrada antes

> **T7a (empata): entre 0 e +1,0 pp.**
> **T7b (acima): entre −1,0 e +0,5 pp — pior que a T7a.**

**Fundamento da direção da T7a:** hoje perdemos 52,4% de um tipo de decisão que
aparece 359 vezes em 3.304 (11% das decisões). Recuperar parte disso deveria
valer algo, mas menos que o T6 — porque a busca **corrige** `ATTACH`: 867
correções contra 23 de `ATTACK`
([`divergencia-com-busca`](../legado/divergencia-com-busca-2026-08-15.md)). **Boa parte do
erro do ranking aqui já é reparada depois.** É exatamente o motivo pelo qual o
T6 escolheu `ATTACK` e `END` e deixou `ATTACH` de fora.

**Fundamento da T7b ser pior:** inverter a precedência troca um viés por outro.
Hoje acertamos 99,7% das decisões em que eles jogam carta; pôr `ATTACH` acima
coloca isso em risco sem nenhuma evidência de que a inversão seja o certo.

**Contra a previsão pesa o histórico:** 20+ hipóteses, 3 sobreviventes — e a
minha previsão de mesa errou três vezes nesta semana e acertou uma.

---

## N, critério e ordem

| | |
|---|---|
| protocolo | `comparar_decks.py --variante-a atual --variante-b …`, **10 réplicas por lado**, n=1100, deck **v7** |
| família | **2 testes** (T7a e T7b), α = 0,025 |
| gate | **conjuntivo**: IC(Bonferroni 2) inteiro acima de zero **E** não regredir em nenhuma das 4 casas |
| custo | ~3,6 h por variante |

**Ordem: T7a primeiro.** A T7b só roda se a T7a passar — não faz sentido testar
a direção de um efeito que não existe. Se a T7a não passar, a T7b não é rodada e
isso fica registrado.

---

## O que falsifica o quê

| observação | o que ela derruba |
|---|---|
| T7a não passa | a intervenção. E é o resultado **esperado** se a busca já repara o erro do ranking — o que seria uma confirmação indireta do `divergencia-com-busca` |
| T7a passa e T7b passa igual | a precedência não importa, só importa **deixar de ser sempre `PLAY`** — e aí o mecanismo é o mesmo do T6, replicado numa quarta fronteira |
| T7a passa e T7b piora | a direção importa: empatar é diferente de inverter |
| as duas regridem numa casa | dependência de matchup, que é a pergunta 70.4 da rubrica |

---

## Riscos declarados

1. **A busca já corrige `ATTACH`.** É o argumento mais forte contra este teste, e
   está registrado antes: 867 correções em 14.926 decisões. Se o ganho do
   ranking for reparado adiante, o painel não verá nada.
2. **Risco de regressão em `PLAY`.** Hoje erramos 0,3% das decisões em que eles
   jogam carta. Mexer na fronteira pode estragar o que já está certo.
3. **O agente está num ótimo local** testado por 20+ hipóteses.

---

## Resultado — **EMPATE**, e era o resultado previsto

10 réplicas por lado, 230 minutos, deck v7:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 53,03% | ± 0,70 pp |
| `t7_attach_empata` | 53,12% | ± 0,70 pp |

| | |
|---|---|
| diferença | **+0,09 pp** (erro padrão 0,31; Welch, 18,0 g.l.) |
| IC 95% | **[−0,56; +0,74]** |
| Bonferroni(2) | [−0,67; +0,85] |
| **veredito** | **empate estatístico — o IC cruza zero** |

Por casa, nenhuma se separa: +0,62, −0,96, +0,03, −0,03, todos com IC cruzando.

**A previsão registrada era "entre 0 e +1,0 pp".** O resultado é **+0,09 pp** —
no piso da faixa. Acertou, mas de um jeito que só é interessante por causa do
motivo.

### Por que este empate vale mais que muitos resultados positivos

O pré-registro declarou o argumento **contra** o próprio teste, antes de rodar:

> *A busca já **corrige** `ATTACH`: 867 correções contra 23 de `ATTACK`. Boa
> parte do erro do ranking aqui já é reparada depois. É exatamente o motivo pelo
> qual o T6 escolheu `ATTACK` e `END` e deixou `ATTACH` de fora.*

E a tabela de falsificação dizia:

> *T7a não passa → a intervenção cai. E é o resultado **esperado** se a busca já
> repara o erro do ranking — o que seria uma confirmação indireta do
> `divergencia-com-busca`.*

**Foi isso.** O ranking erra 52,4% das decisões de anexar energia; corrigi-lo não
move o resultado, porque a busca já reparava.

### E isso fecha um par controlado com o T6

Os dois testes têm a **mesma forma** — mover um tipo de jogada na escada de
prioridade — e diferem numa única variável conhecida de antemão: **se a busca
repara aquele tipo**.

| teste | tipo movido | correções da busca | efeito no painel |
|---|---|---:|---:|
| **T6** | `ATTACK` / `END` | **23** e 58 | **+1,03 pp**, gate PASSA |
| **T7a** | `ATTACH` | **867** | **+0,09 pp**, empate |

**A busca repara → mexer no ranking não paga. A busca não repara → paga.** É uma
comparação controlada, e nenhum dos dois resultados foi olhado antes de o outro
ser previsto.

Isso também explica, retroativamente, **por que a compressão uniforme falhou**:
ela mexia nos quatro tipos, dois dos quais a busca já corrigia. O ruído somado ao
sinal tem agora um número.

### T7b não foi rodada

O pré-registro declarou: *"a T7b só roda se a T7a passar — não faz sentido testar
a direção de um efeito que não existe. Se a T7a não passar, a T7b não é rodada e
isso fica registrado."*

**Fica registrado.** Economizados 3,6 h de máquina por uma regra escrita antes.

### O que fica no código

`PTCG_PRIO_ATTACH` permanece, **com o padrão 50,0** — o valor de sempre. A
variante fica alcançável e o número dela está neste documento, como manda a
Parte 1.1 do plano-mestre: resultado negativo fica no código, desligado, com a
medição no comentário.
