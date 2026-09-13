> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T16 — nocautear tira recurso dele, e isso não vale nada hoje: **pré-registro**

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.**
>
> Vem do Fernando, palavra por palavra: *"matar um pokemon já deveria ser
> relevante pra ele... se for ex ou tiver energia, mais ainda pois tira mais
> recurso do oponente."*

---

## Primeiro, o que dessa intuição já está resolvido

| a intuição | o que o código faz hoje |
|---|---|
| matar deveria ser relevante | **é o termo dominante**: `(prêmios_dele − prêmios_meus) × 1000`. Nocaute = prêmio = **+1.000** |
| ex deveria valer mais | **já vale 2.000**, sem código extra — ex dá 2 prêmios, e o termo conta cartas de prêmio |
| **tirar energia dele deveria valer** | **não existe em lugar nenhum** |

**Dois terços da intuição já estavam implementados.** Este teste é sobre o terço
que não estava.

---

## E o agente age mesmo assim? Medido, 90 partidas

Antes de mexer no peso, a pergunta certa é se o agente **usa** o que já vale
1.000. [`medir_letal.py`](../../tools/medir_letal.py), 2.009 decisões:

| | |
|---|---:|
| turnos com nocaute ao alcance | **917** |
| o agente chegou nele | **916 — 99,9%** |
| turnos com vitória ao alcance | 553 |
| o agente fechou | **552 — 99,8%** |

E por prêmios restantes do adversário, sem buraco em nenhuma faixa:

| prêmios dele | nocaute ao alcance | achou | perdeu |
|---:|---:|---:|---:|
| 2 | 111 | 111 | **0** |
| 4 | 153 | 153 | **0** |
| 6 | 653 | 652 | 1 |

> **O agente não perde nocautes.** Um comentário antigo no código dizia *"das
> 247 chances de nocaute o agente perde 42"* — **isso é de um agente que não
> existe mais**, e fica retratado aqui.

**Consequência para este teste:** se o termo mudar alguma coisa, será na
**escolha de alvo** e no **timing**, nunca em achar o nocaute. Isso derruba a
versão otimista da hipótese antes de medir.

---

## O que se testa

`PTCG_ENERGIA_DELE_CONTRA=1` — a energia no ativo dele conta **contra** nós.

```python
s -= _conta_energia(ativo_dele) * W_ENERGIA
```

**É o sinal invertido do T14a**, e a inversão é a hipótese inteira:

| | efeito no score |
|---|---|
| **T14a** (morto): `+energia(dele)` | premiava o inimigo **ter** energia → **desestimulava** nocautear |
| **T16**: `−energia(dele)` | alvo carregado vivo vale −45; nocauteado, ele promove com 0 → **premia** matar quem está carregado |

**Peso derivado, não escolhido:** o mesmo `W_ENERGIA` = 15 que já vale para a
nossa energia. Se uma energia nossa vale 15, uma energia dele destruída vale 15.

**Por que não repete o erro do T14a:** lá o termo apontava para o lado errado —
matar apagava o que ele premiava. Aqui matar **realiza** o que ele premia.

**Por que não repete o erro do T14b:** o banco dele é incontrolável. A energia
do ativo dele **é** controlável — o nosso nocaute é exatamente o que a apaga.

Isso põe o T16 do lado certo da regra que o T14 produziu: *a avaliação de estado
só paga quando corrige algo que o agente controla.*

---

## A previsão, registrada antes

> **Entre −0,6 e +0,4 pp, e o mais provável é empate.**

**Fundamento do lado do empate, que é o esperado:** o nocaute já vale 1.000 e o
agente já pega 99,9% deles. O termo pesa 1,11 × 15 ≈ **17 pontos**, que é
**1,7%** do prêmio. Ele não vai mudar *se* nocauteamos. Sobra alvo e timing, e
o nosso deck tem um ativo só na maior parte dos turnos.

**Fundamento do lado positivo:** é a única parte da mecânica de recurso que a
avaliação não enxerga, é controlável, e o peso não foi inventado.

**Contra a minha própria previsão:** eu errei o **sinal** no T13b, e minhas
previsões erraram 3 das últimas 6. Prever "inerte" por argumento foi
exatamente o que eu fiz no T15 — e o T15 mostrou que o argumento estava certo
no veredito e **errado na magnitude** (esperava até −3,0; deu −0,22).

| observação | leitura |
|---|---|
| **IC acima de zero** | tirar recurso dele vale, e a intuição do Fernando achou um buraco real. **Réplica antes de adotar** |
| **empate** | o termo é inerte porque o prêmio já domina. **Registrar e não adotar** |
| **negativo** | penalizar o que ele tem desvia o agente do que nós controlamos — e aí a regra do T14 vale para os **dois** sinais |

**Protocolo:** `comparar_decks.py --variante-a atual --variante-b t16_energia_dele_contra --a decks/ogerpon_v9.csv --replicas 20 --n 1100`. Família de 1. **20 réplicas**. ~6,4 h.

---

## ⚠ O que este teste NÃO vai responder

**O déficit de ataque.** O agente ataca 2,5× menos que pilotos ≥ 1.000 e agora
sabemos que **não é nocaute perdido** — ele pega 99,9%. Os ataques que faltam
são os que **não matam**, e o T15 acabou de medir que premiá-los é inerte
(−0,22 pp).

Duas explicações sobrevivem, e nenhuma é testável com um termo novo:

1. **os ataques que faltam não valem** para este deck — o Myriad Leaf Shower
   escala com energia anexada, então construir antes pode ser a jogada certa;
2. **valem, e o que falta é a busca**, não o objetivo.

A segunda é a única frente grande que continua aberta no agente.

---

## Resultado — **empate**, e a previsão acertou ponto e veredito

> **Nota de procedência.** A rodada terminou sozinha às **23h00 de 26/08** (428
> min, 20 réplicas completas). A sessão que a vigiava caiu antes de colher o
> log, e o veredito ficou **dois dias sem registro**. Os números abaixo foram
> lidos de `logs/t16.log` em **28/08**, sem reexecutar e sem editar nada — a
> rodada é a pré-registrada, com o protocolo pré-registrado.

20 réplicas alternadas A, B, A, B, 428 minutos:

| | vitórias |
|---|---:|
| `atual` | 55,14% ± 0,54 pp |
| `t16_energia_dele_contra` | 55,24% ± 0,51 pp |

| | |
|---|---|
| efeito de **ligar** o termo | **+0,10 pp** |
| IC 95% | **[−0,24; +0,43]** |
| erro padrão | 0,17 pp (Welch, 37,8 g.l.) |
| veredito | **empate estatístico** |

A previsão registrada era **−0,6 a +0,4 pp, e o mais provável é empate**. Deu
**+0,10 pp**, empate — **dentro da faixa, e no veredito certo**.

**E é um nulo informativo, não um "não sei".** O IC tem 0,67 pp de largura: ele
descarta qualquer ganho acima de **~0,43 pp**. O termo não é pequeno-e-talvez —
ele é inerte no tamanho que importaria.

### O mesmo ponto do T14b, no sinal oposto e no lado oposto do campo

| teste | o que descreve | efeito de ligar |
|---|---|---:|
| **T14b** | o **banco** dele conta contra | **+0,10 pp** [−0,30; +0,49] |
| **T16** | a **energia do ativo** dele conta contra | **+0,10 pp** [−0,24; +0,43] |

Dois termos diferentes, sobre partes diferentes do lado dele, com pesos
diferentes, deram **o mesmo ponto e o mesmo veredito**. Isso é a terceira
confirmação da regra que o T14 produziu: *a avaliação de estado só paga quando
corrige algo que o agente controla* — e agora ela vale mesmo quando o termo
aponta para o **lado certo** e descreve algo **controlável**, porque o prêmio
de 1.000 já esgotou o que havia para ganhar ali.

**O fundamento pré-registrado do lado do empate era exatamente esse**, e
sobreviveu: o termo pesa ~17 pontos contra um prêmio de 1.000 (1,7%), e o
agente já pega **99,9%** dos nocautes. Não havia decisão para virar.

### Por casa — e a única que se move é uma régua quebrada

| casa | `atual` | com o termo | efeito de ligar | IC 95% |
|---|---:|---:|---:|---|
| `ref950+Lucario 0,05s` | 36,29% | 35,90% | −0,39 | [−1,16; +0,38] |
| `ref950+Lucario 0,5s` | 36,34% | 36,27% | −0,07 | [−0,96; +0,82] |
| **`ref950+sample`** | 71,95% | **72,82%** | **+0,87** | **[+0,24; +1,50]** |
| `primeira (piso)` | 76,01% | 75,95% | −0,05 | [−0,78; +0,67] |

**O gate não se aplica** — ele só julga casas depois que o agregado aponta
vencedor, e não apontou.

E a casa que se moveu **não conta como evidência a favor**, por dois motivos
declarados antes de eu olhar para ela:

1. **É a régua quebrada nº 2.** `ref950+sample` é a política forte com o
   **deck desencaixado**; ela já está no livro-razão como instrumento que mede
   outra coisa.
2. **São quatro casas.** Um IC de 95% fora do zero em uma de quatro é o que se
   espera do acaso com alguma frequência, e a regra da casa é Bonferroni **pela
   família declarada** — a família aqui é 1 teste no agregado, não 4 casas
   garimpadas depois.

Ler esse +0,87 como descoberta seria exatamente o jardim de caminhos que se
bifurcam que a regra nº 5 proíbe.

### Veredito: **não adotado**, e a flag continua desligada

Pela tabela pré-registrada: *"empate → o termo é inerte porque o prêmio já
domina. **Registrar e não adotar**"*. `ENERGIA_DELE_CONTRA` fica em `0`, como
nasceu.

**A intuição do Fernando estava certa em dois terços e o terço que faltava não
tinha valor a colher** — não porque a ideia fosse errada, mas porque o objetivo
já pagava 1.000 pelo mesmo evento, e o agente já cobrava esse cheque em 99,9%
das vezes.

### O que este resultado fecha

**A fila de termos de avaliação está vazia, e agora está vazia por medição.**
O placar por lado do tabuleiro, contando só o que foi medido:

| termos que descrevem… | testes | placar |
|---|---|---|
| **o nosso lado** | T6, T10, T13 | **3 aprovados de 3** |
| **o lado dele, ou o dano** | dano absoluto (−11,46), dano fração (−7,37), T15 (−0,22), T14a (morto por construção), T14b (+0,10), **T16 (+0,10)** | **0 aprovados de 6** |
 O déficit de ataque deixa de ter candidato
na avaliação: ou os ataques que faltam não valem para este deck, ou o gargalo
é a **busca**. Nenhuma das duas se resolve com um termo novo.
