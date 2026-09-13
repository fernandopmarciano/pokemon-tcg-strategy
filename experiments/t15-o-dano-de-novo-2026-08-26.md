> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T15 — reabrir o dano, num agente que não é mais o mesmo: **pré-registro**

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.**
>
> ⚠ **E isto reabre uma hipótese REPROVADA DUAS VEZES.** O motivo para reabrir
> está declarado abaixo, e se ele não convencer, o teste não deve rodar.

---

## O buraco que sobrou

O agente **ataca 2,5× menos** que pilotos ≥ 1.000 nas mesmas posições:

| | eles | nós |
|---|---:|---:|
| ATTACK | **12,1%** | **4,8%** |

O T13 mal moveu (0,39× → 0,43×). O T14 não tocou. **É o maior desvio de
comportamento que continua aberto**, e a causa está isolada: **o agente não
enxerga o dano que causa.**

```python
USAR_DANO_REAL   = os.environ.get("PTCG_DANO_REAL", "0") == "1"
USAR_DANO_FRACAO = os.environ.get("PTCG_DANO_FRACAO", "0") == "1"
```

Atacar sem nocautear **não muda a nota** do estado. O agente ataca porque sobrou
ataque, não porque atacar vale.

---

## Por que reabrir algo reprovado duas vezes

| forma | efeito medido | quando |
|---|---:|---|
| dano absoluto × `W_DANO` | **−11,46 pp** [−17,28; −5,63] | antes de 18/08 |
| fração derrubada × `W_KO` | **−7,37 pp** [−10,02; −4,73] | antes de 18/08 |

**O motivo registrado da falha:**

> *"premiar dano parcial empurra o agente a **atacar cedo**, e atacar encerra o
> turno. Foi a mesma medição que já tinha custado 57,6 pp quando `ATTACK` estava
> no topo da L0."*

**A falha era de INTERAÇÃO com a escada de prioridades** — e essa escada mudou
três vezes desde então:

| | o que mudou | quando |
|---|---|---|
| **T6** | `ATTACK` subiu de 12 para 31 e `END` de 8 para 29 | 19/08 |
| **T10** | energia no banco parou de contar | 23/08 |
| **T13** | vida parou de pagar por rotação | 25/08 |

**O T6 é o que importa aqui:** ele reequilibrou exatamente a dimensão
"atacar cedo × desenvolver primeiro" que fez o dano falhar. A medição de −7,37
pp vale para um agente em que `ATTACK` valia 12 e a rotação pagava +150.
**Esse agente não existe mais.**

> **Uma medição vale para o estado em que foi feita.** Este é o princípio que o
> projeto aplicou ao retratar o teto do deck, a dispersão e o "46,3% de dois
> ataques". Aplicá-lo aqui é consistência, não teimosia.

---

## A intervenção, e por que só uma forma

`PTCG_DANO_FRACAO=1` — a fração já derrubada do ativo dele, multiplicando
`W_KO`, limitada a 1.

**Só esta, e não a absoluta.** O motivo é do próprio código:

> *"A forma absoluta viola a ordem da própria avaliação: um ativo com 190 de dano
> marcado vale 380 e derrubá-lo vale `W_KO` = 300, então a avaliação paga mais
> por **deixar** o adversário quase morto."*

A forma em fração não tem esse defeito: um alvo a 90% vale **0,9 de um nocaute**,
e nunca mais que um nocaute. **É a única das duas que é coerente**, e foi a que
perdeu menos (−7,37 contra −11,46).

Nenhum peso novo: reusa `W_KO` = 300, que já existe.

---

## ⚠ Fui medir a divergência antes do painel e a régua quebrou na mão

O plano era o de sempre: rodar a triagem barata, e só gastar bancada se o termo
mudasse mais de 5% das decisões. Desta vez a ferramenta virou
[`muda_a_escolha.py`](../../tools/muda_a_escolha.py) — e eu pus nela **um controle
que as três medições anteriores não tinham**: comparar o baseline **consigo
mesmo**.

```
decisoes nossas             : 893  (3 mundos cada = 2679 pares)
CONTROLE baseline x baseline:  482    18,0%   [16,6; 19,5]
baseline x t15_dano_fracao  :  480    17,9%   [16,5; 19,4]
```

**Duas chamadas idênticas do agente discordam em 18% das decisões.** E o número
da variante é indistinguível disso.

### Os quatro números que eu usei como critério eram o próprio ruído

| teste | divergência que eu reportei | piso de ruído medido agora |
|---|---:|---:|
| T10 | 23,5% | ~18–22% |
| T13 | 20,9% | ~18–22% |
| T14a | 19,3% | ~18–22% |
| T14b | 18,5% | ~18–22% |

**Os quatro estão dentro da faixa do controle.** A régua que eu criei nesta
sessão, chamei de disciplina nova do projeto e apliquei três vezes estava
medindo a loteria interna do agente.

### A causa, e por que não tem conserto

Está escrita no próprio agente: a determinização **sorteia** — `random.shuffle`
do meu deck e um arquétipo do meta pela fatia de uso — **a cada chamada**. O
agente é uma **política estocástica por desenho**.

Tentei congelar com `random.seed()` antes de cada chamada. Não bastou:

| modo | divergência baseline × baseline |
|---|---:|
| como está | **21,8%** |
| determinização fixa (`PTCG_DETERMINIZACAO=ordem`) | **13,8%** |
| orçamento de 60 s em vez de 2 s | **22,4%** |

O relógio **não** é a causa. A determinização responde por uns 8 pontos. **Os
13,8% que sobram não saem com semente do Python** — a busca do engine tem
aleatoriedade própria, fora do módulo `random`. **`agent()` não é determinizável
de fora.**

### O que sobra, e o que não sobra

**Sobra uma leitura só:** muito **abaixo** do piso significa inerte. Foi o caso
da P1 — 0,5% contra um piso de ~18%. Um termo que não move a escolha nem tanto
quanto a loteria move sozinha não vai aparecer em lugar nenhum.

**Não sobra a leitura que eu vinha usando.** E não adianta subtrair o piso:
decisões apertadas trocam **pelos dois motivos ao mesmo tempo** — a loteria e o
termo agem exatamente nas mesmas posições — então a medida **satura onde o termo
atuaria**. "Acima do piso" não vira estimativa de nada.

> **Régua quebrada nº 10.** As três adoções (T10, T13, T14b) foram decididas
> pelo **painel**, por vitória, com intervalo — nada muda nelas. O que cai é a
> justificativa barata que eu dava para gastar a bancada.

### E este teste roda mesmo assim

Com a triagem morta, a decisão de gastar 7,2 h se apoia **no argumento**, que
está escrito acima e é anterior a qualquer medição: o déficit de ataque é o
maior desvio aberto, a causa está isolada, e a condição que explicava a
reprovação mudou de forma verificável. **A previsão registrada não muda.**

---

## A previsão, registrada antes

> **Entre −3,0 e +0,5 pp.** Faixa larga e assimétrica para baixo.

**Fundamento do lado negativo, que é o lado provável:** a hipótese já perdeu
duas vezes, e perdeu feio. O mecanismo da falha (atacar cedo demais) não some
só porque a escada mudou — o T6 reequilibrou, não inverteu.

**Fundamento do lado positivo:** o desvio de comportamento é grande e medido
(2,5× menos ataque), a causa está isolada, e a condição que explicava a falha
mudou de forma verificável. Se o dano for reabilitável, é aqui.

**Contra a previsão:** minhas previsões erraram 3 das últimas 5, e a última que
errei foi de **sinal**.

| observação | leitura |
|---|---|
| **IC acima de zero** | o dano era reabilitável, e a falha era de interação com o T6. **Réplica antes de adotar** |
| **empate com IC estreito** (< 0,9) | o termo virou inerte — nem ajuda nem atrapalha. **Não adotar**, e o déficit de ataque continua sem explicação acionável |
| **negativo** | a reprovação se mantém no agente novo. **Fecha o assunto para valer**, e o déficit de ataque passa a ser aceito como propriedade do desenho |

**Protocolo:** `comparar_decks.py --variante-a atual --variante-b t15_dano_fracao --a decks/ogerpon_v9.csv --replicas 20 --n 1100`. Família de 1. **20 réplicas**. ~7,2 h.

---

## O que este teste NÃO é

1. **Não é varrer o peso.** Uma forma, um peso, o que já existe. Se passar, a
   réplica muda a configuração — não o valor até achar um que funcione.
2. **Não contradiz a regra do T14.** Dano causado é consequência direta de uma
   ação **nossa** — está do lado do que o agente controla. O que falhou no T14
   foi descrever o estado **dele** por coisas que não dependem de nós.

---

## Resultado — **empate**, e o empate prova que a reabertura estava certa

20 réplicas alternadas, 382 minutos:

| | vitórias |
|---|---:|
| `atual` | 55,30% |
| `t15_dano_fracao` | 55,08% ± 0,77 pp |

| | |
|---|---|
| efeito de **ligar** o termo | **−0,22 pp** |
| IC 95% | **[−0,67; +0,24]** |
| erro padrão | 0,23 pp (Welch, 37,0 g.l.) |
| veredito | **empate estatístico** |

A previsão registrada era **−3,0 a +0,5 pp**. Deu **−0,22** — dentro da faixa.

### O número que importa não é o −0,22. É a comparação com o −7,37

| quando | mesmo termo, mesma forma | efeito |
|---|---|---:|
| antes de 18/08 | `DANO_FRACAO` ligado | **−7,37 pp** [−10,02; −4,73] |
| **hoje** | `DANO_FRACAO` ligado | **−0,22 pp** [−0,67; +0,24] |

**O mesmo termo, no mesmo agente, com o mesmo peso, passou de custar 7,4 pontos
para custar zero.** Nada mudou nele — mudou o que estava em volta.

**A justificativa registrada para reabrir era exatamente essa:** a falha não era
do termo, era da **interação com a escada de prioridades**, e o T6 reequilibrou
a escada em 19/08 (`ATTACK` 12 → 31, `END` 8 → 29). O mecanismo previsto
(*"premiar dano empurra o agente a atacar cedo, e atacar encerra o turno"*)
**deixou de existir quando atacar parou de ser barato**.

> Isto é a confirmação mais forte que o projeto produziu do princípio *"uma
> medição vale para o estado em que foi feita"*. A reprovação de −7,37 pp era
> **verdadeira e obsoleta ao mesmo tempo**.

### Mas continua não adotado, e por dois motivos

1. **Empate.** O IC cruza zero, e o ponto é negativo.
2. **Regride numa casa.** Contra a política nula, `atual` ganha **+0,83 pp**
   [+0,23; +1,43] — fora do zero. Pelo gate conjuntivo isso é veto, mesmo que o
   agregado tivesse apontado vencedor.

Pela tabela pré-registrada: *"empate com IC estreito → o termo virou inerte.
**Não adotar**, e o déficit de ataque continua sem explicação acionável"*.

**Nota de honestidade sobre o meu pré-registro:** eu escrevi "IC estreito
(< 0,9)" e a largura deu **0,91**. Fica na fronteira da minha própria regra. Nas
duas leituras a ação é a mesma — não adotar — mas registro que a régua ficou
ambígua **de novo**, pela segunda vez (a primeira foi o T13c).

---

## E o déficit de ataque agora tem uma explicação a menos

Depois deste teste, medi a coisa que faltava
([`t16`](t16-o-que-o-nocaute-destroi-2026-08-26.md)):

| | |
|---|---:|
| turnos com nocaute ao alcance | 917 |
| **o agente chegou nele** | **916 — 99,9%** |
| turnos com vitória ao alcance | 553 |
| **o agente fechou** | **552 — 99,8%** |

**O agente não perde nocautes.** Então os ataques que faltam, comparado a
pilotos ≥ 1.000, são os que **não matam** — e premiá-los é o que este teste
acabou de medir como inerte.

Sobram duas explicações, e nenhuma se resolve com um termo novo na avaliação:

1. **os ataques que faltam não valem** para este deck (o Myriad Leaf Shower
   escala com energia anexada, então construir pode ser certo);
2. **valem, e o gargalo é a busca**, não o objetivo.
