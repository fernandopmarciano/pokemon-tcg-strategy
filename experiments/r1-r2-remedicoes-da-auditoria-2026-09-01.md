# R1 e R2 — as duas remedições da auditoria de 28/08 — **pré-registro**

> **Escrito antes de a primeira rodada começar.** O resultado entra numa seção
> no fim, **sem editar nada acima desta linha.**
>
> **Categoria C — auditoria.** Nenhuma das duas muda o agente: as duas
> remedem números que o relatório **já publica**. A fila de termos de avaliação
> continua vazia e nada aqui a reabre.

## Por que estas duas, e por que agora

A [auditoria de 28/08](../auditoria-2026-08-28.md) encontrou três defeitos.
O segundo já foi corrigido no código (`politica_15_08` passou a fixar
`PTCG_HP_INVARIANTE=0`). Os outros dois são **números publicados medidos com
régua errada ou em versão errada**, e só uma rodada os conserta.

A Simulation encerrou em 31/08. **Estas são as duas últimas medições capazes de
mudar um número do relatório** — depois delas o projeto é só texto.

**Sem Bonferroni.** `--familia 1` nas duas: são remedições independentes de
números já publicados, com previsão pontual escrita, não uma varredura em busca
do melhor. A família declarada tem tamanho 1 em cada.

---

## R1 — o prior, medido com a régua que o projeto aposentou

**O defeito.** O prior vale **+10,11 pp** [+8,59; +11,64] — o maior número do
agente. Ele é de **12/08** e foi medido no `painel.py`, que o projeto
**aposentou em 22/08** para decidir variante de agente (régua quebrada nº 9:
sobredispersão de 1,39×, IC 39% estreitos). O relatório afirma as duas coisas
ao mesmo tempo, e um avaliador acha a contradição sem ajuda.

```
python tools/comparar_decks.py --variante-a atual --variante-b sem_prior \
    --a decks/ogerpon_v9.csv --replicas 10 --n 1100 --familia 1
```

`sem_prior` é `{"PTCG_W_PRIOR": "0"}` e existe desde 12/08 — o defeito nunca foi
falta de ferramenta, foi a ferramenta nova nunca ter sido apontada para o número
velho.

### Previsão

**Ponto entre +7,5 e +12,5 pp, e o IC inteiro acima de +5 pp.** O raciocínio: 10
pp é ~11× a resolução da bancada (0,91 pp com 10 réplicas), então o ponto deve
sobreviver; o IC deve sair **mais largo** que o publicado, porque é exatamente a
sobredispersão de 1,39× que o painel escondia.

### Tabela de falsificação

| resultado | leitura |
|---|---|
| ponto ≥ +7,5 pp, IC todo > 0 | **o número sobrevive.** Trocar a fonte nos 6 documentos: o valor passa a vir de réplicas, não do painel |
| ponto entre +3 e +7,5 pp | sobrevive em sinal, mas **o relatório publica número inflado** — corrigir o valor onde ele aparece |
| IC cruza zero | **o maior número do agente cai.** Reescrever a §6 do relatório, que hoje diz "ali vale +10,11 pp" |
| ponto negativo | o prior é dano, e isso é frente nova — grande demais para 12 dias |

---

## R2 — o T12, remedido com a variante consertada

**O defeito.** O relatório diz *"medimos +2,56 pp [+1,90; +3,22] de ganho só na
política sobre o agente que está na ladder"*. O T12 rodou em **23/08**; o **T13
foi adotado em 25/08** e vale **+0,59 pp** [+0,09; +1,09]. O número publicado
**não inclui uma mudança adotada**, e por isso está defasado **para baixo**.

Comando idêntico ao do T12 original — só a variante mudou (agora fixa
`HP_INVARIANTE=0`, sem o que ela herdava o T13 ligado nos dois lados):

```
python tools/comparar_decks.py --variante-a politica_15_08 --variante-b atual \
    --a decks/ogerpon_v9.csv --replicas 10 --n 1100 --familia 1
```

### Previsão

**Ponto entre +2,6 e +3,7 pp, esperado ~+3,15.** Se os ganhos somassem, seria
2,56 + 0,59 = **3,15 pp**. Mas o próprio T12 mediu que **a sinergia não está
estabelecida** (a diferença para a soma deu +0,65 [−0,48; +1,78]), então a soma
é a expectativa, não a garantia.

### Tabela de falsificação

| resultado | leitura |
|---|---|
| ponto ≥ +2,56 pp | **confirma a auditoria**: o relatório publicava menos do que temos. Atualizar a frase da §8 |
| ponto entre +1,90 e +2,56 pp | dentro do IC antigo — o T13 **não aparece** no agregado. A frase do relatório fica como está, com nota de que o T12 foi reexecutado |
| ponto < +1,90 pp | contradiz o T12 original **ou** o T13. **Não publicar nada** antes de entender qual dos dois |

---

## Protocolo

**Em sequência, nunca em paralelo.** Armadilha nº 4 do projeto: carga externa
cai inteira em quem estiver rodando e vira diferença sistemática. O
`comparar_decks.py` alterna A, B, A, B justamente para diluir deriva — duas
rodadas simultâneas quebrariam isso nas duas.

Ordem: **R1 primeiro.** É o número mais espalhado (relatório, checklist de
submissão e cinco documentos do legado); se surpreender, quero o máximo de dias
para reagir.

`submission/main.py` **não é editado** enquanto qualquer uma rodar — cada worker
importa o arquivo do disco quando sobe (armadilha nº 3).

| | |
|---|---|
| custo estimado | ~3,6 h cada, ~7,2 h no total |
| lançado em | 01/09/2026 |
| logs | `logs/r1_prior.log`, `logs/r2_t12.log` |

---

# Resultado da R1 — **o sinal inverteu, e a previsão falhou na quarta linha**

> Escrito em 01/09, com a rodada terminada. Nada acima desta linha foi editado.

10 réplicas × 1.100 partidas por lado, **177 min**. `logs/r1_prior.log`.

| variante | agregado | dispersão (n=10) |
|---|---:|---:|
| `atual` (prior ligado, `W_PRIOR`=10) | **55,10%** | ± 0,55 pp |
| **`sem_prior`** (`W_PRIOR`=0) | **55,81%** | ± 0,48 pp |

| | |
|---|---|
| diferença | **−0,71 pp** contra o prior |
| erro padrão | 0,23 pp (Welch, 17,7 g.l.) |
| **IC 95%** | **[−1,20; −0,22]** — não cruza zero |
| gate | **PASSA para `sem_prior`**: vence no agregado e não regride em nenhuma das 4 casas |

| casa | `atual` | `sem_prior` | A−B |
|---|---:|---:|---:|
| ref950+Lucario 0,05s | 36,19% | 36,46% | −0,27 [−1,21; +0,66] |
| ref950+Lucario 0,5s | 35,78% | 36,88% | −1,10 [−2,54; +0,34] |
| ref950+sample | 72,05% | 72,66% | −0,62 [−2,05; +0,81] |
| primeira (piso) | 76,40% | 77,15% | −0,75 [−1,57; +0,08] |

## Contra a tabela de falsificação: **a quarta linha**

A previsão era *"ponto entre +7,5 e +12,5 pp, IC inteiro acima de +5"*. Saiu
**−0,71 pp**. Não é a terceira linha (IC cruzando zero) — é a **quarta**, a que
eu escrevi como *"o prior é dano, e isso é frente nova"*.

**Errei o sinal, e não por pouco.** É a quinta vez em oito que erro a magnitude,
e a primeira em que erro o **sentido** com o intervalo inteiro do outro lado.

## O instrumento está são — três verificações antes de acreditar

Regra nº 7: quando um número surpreende, a primeira hipótese é a régua.

1. **A variante faz o que diz.** `sem_prior` é `{"PTCG_W_PRIOR": "0"}` e nada
   mais; `atual` é `{}` e herda `W_PRIOR = 10.0` de `main.py:3320`. Não há a
   armadilha do `politica_15_08` (herdar flag adotada depois) porque a única
   flag em jogo é fixada explicitamente de um lado e default do outro.
2. **A dispersão bate.** ± 0,55 e ± 0,48 pp contra os ~0,725 pp típicos.
3. **O controle indireto fecha.** `atual` deu **55,10%** hoje contra **54,44%**
   no T12 (23/08) — **+0,66 pp**, e o T13 (adotado em 25/08, entre as duas
   medições) vale **+0,59 pp** [+0,09; +1,09]. A bancada reproduziu uma mudança
   conhecida no valor certo, sem que ninguém lhe pedisse.

## O que mudou entre 12/08 e hoje: **o agente, não a régua**

Em 12/08 o painel mediu `sem prior` em **38,0%** e o prior em **48,9%**.

| | 12/08 | 01/09 | Δ |
|---|---:|---:|---:|
| `sem_prior` | 38,0% | **55,81%** | **+17,8 pp** |
| com prior | 48,9% | 55,10% | +6,2 pp |

**O agente sem prior melhorou quase três vezes mais do que o agente com prior.**
Entre as duas medições entraram T1, T6, T8, T9, T10 e T13, e o deck foi de v6
para v9 — e o **T6 reequilibrou a escada de prioridades** (`ATTACK` 12 → 31,
`END` 8 → 29), que é exatamente onde o prior atuava.

**A leitura:** o prior era a peça que segurava um agente cuja escada estava mal
calibrada. Consertada a escada, ele deixou de pagar.

⚠ **A comparação entre datas não é pareada** — as casas do painel mudaram em
23/08. Os 38,0% e 48,9% ilustram a direção; **o que decide é a linha de hoje**,
medida com as casas de hoje e com réplicas.

### E é o T6 invertendo o segundo veredito

O termo de dano saiu de **−7,37 pp** para **−0,22 pp** *sem mudar uma linha*,
porque o T6 mudou a escada entre as duas medições. Agora o prior faz o caminho
inverso, pela **mesma causa**. Duas inversões, um culpado.
**Toda medição vale para a versão em que foi feita** deixa de ser regra escrita
e passa a ser resultado medido duas vezes, em direções opostas.

## O que este resultado NÃO autoriza dizer

- **Não** autoriza *"o prior faz mal"*. O efeito é **−0,71 pp**, menor que a
  resolução declarada da bancada (**0,91 pp** com 10 réplicas). O IC não cruza
  zero nesta rodada porque a dispersão saiu abaixo da média, não porque o efeito
  seja grande. A leitura sustentada é **"o prior não vale nada no agente de
  hoje"**.
- **Não** é adoção. Regra nº 3: replicar antes de adotar, com configuração
  diferente. E não há o que adotar — o agente está congelado e a Simulation
  fechou em 31/08.
- **Não** invalida o treino do prior, auditado e limpo em 28/08 (split por
  episódio, learning-to-rank, duas linhas de base).

## O que ele obriga a mexer no relatório

| onde | o texto diz | estado |
|---|---|---|
| §6 | *"Onde ele vale? Em atravessar fronteiras de tipo — e ali vale **+10,11 pp**"* | **falso para o agente atual** |
| §4 | a determinização corrigida fez *"a avaliação aprendida valer **6×** o que medíramos"* (+1,65 → +10,11) | o 6× era real **em 12/08**; hoje o denominador da frase não existe mais |
| `CONTINUAR-AQUI`, checklist de submissão, 5 documentos do legado | *"+10,11 pp"* | mesma correção |

E abre a leitura que **fortalece** a §6 em vez de enfraquecê-la: a seção já
mostrava o modelo empatando com *"escolha sempre a primeira opção"* em três
amostras. A única defesa que sobrava era *"mas ele vale 10 pp atravessando
tipos"*. **Essa defesa caiu com a régua certa.**

---

# R2 — **interrompida em 7 de 10 réplicas.** Parcial registrado, resultado NÃO declarado

> Escrito em 01/09, com a rodada morta por causa **externa** — não por ninguém
> ter olhado o número. Nenhum processo sobreviveu. `logs/r2_t12.log`, 141 min.

## A regra de leitura, escrita ANTES de relançar

O pré-registro pede **10 réplicas**. Aceitar 7 porque o parcial está bonito é
**parada opcional**, e é a mesma família de erro que o projeto já catalogou no
jardim de caminhos que se bifurcam.

**Fica declarado agora:** se a R2 for relançada, **o resultado que vale é o da
rodada completa de 10 réplicas**, e o parcial abaixo permanece como registro
histórico — não entra no relatório, não é citado como medição, e **não** é
combinado com a rodada nova.

## O parcial, para não se perder

7 réplicas pareadas completas, alternadas A, B, A, B.

| variante | agregado | dispersão (n=7) |
|---|---:|---:|
| `politica_15_08` (corrigida, `HP_INVARIANTE=0`) | 51,61% | ± 0,74 pp |
| `atual` | 55,13% | ± 0,54 pp |

| | |
|---|---|
| diferença | **+3,51 pp** a favor da política atual |
| erro padrão | 0,35 pp (Welch, 11,0 g.l.) |
| IC 95% | [+2,75; +4,28] |

Contra o publicado (**+2,56 pp** [+1,90; +3,22]) e contra a previsão
pré-registrada (+2,6 a +3,7, esperado ~+3,15): **o parcial cai dentro da faixa
prevista e acima do número que o relatório publica** — que é exatamente o que a
auditoria de 28/08 afirmou que aconteceria.

## ⚠ E ele traz um controle que vale mais que ele: **a bancada reproduziu**

| rodada | `atual` | réplicas |
|---|---:|---:|
| **R1** (01/09) | **55,10%** ± 0,55 | 10 |
| **R2 parcial** (01/09) | **55,13%** ± 0,54 | 7 |

**Duas rodadas independentes, a mesma variante, 0,03 pp de diferença.** Não foi
pedido a ninguém: a bancada mediu a mesma coisa duas vezes e devolveu o mesmo
número. Isso é evidência direta de que a aparelhagem que produziu a inversão da
R1 está estável — e é o tipo de controle que o projeto passou vinte dias
aprendendo a exigir.

---

# R1b — a réplica do prior — **pré-registro**

> Escrito em 02/09, **antes de a rodada começar**. O resultado entra numa seção
> no fim, sem editar nada acima desta linha.

## Por que replicar

Regra nº 3: **replicar antes de adotar, com configuração diferente.** Aqui não
há adoção — o agente está congelado e a Simulation encerrou em 31/08. Mas há
**publicação**, e o número da R1 reescreve a §6 do relatório, o
`CONTINUAR-AQUI`, o checklist de submissão e cinco documentos do legado. Um
número que derruba outro número publicado merece a mesma régua que uma adoção.

E há a razão específica: **a R1 mediu −0,71 pp, e a resolução declarada da
bancada é 0,91 pp com 10 réplicas.** O IC não cruzou zero porque a dispersão
daquela rodada saiu abaixo da média (± 0,55 e ± 0,48 contra ~0,725 típicos).
Um efeito abaixo da resolução, medido uma vez, é candidato a não replicar.

## A configuração diferente

```
python tools/comparar_decks.py --variante-a atual --variante-b sem_prior \
    --a decks/ogerpon_v9.csv --replicas 10 --n 1600 --familia 1
```

**`--n` 1100 → 1600**, mantendo 10 réplicas. É o eixo que o projeto já usou para
desmascarar o *"+2,33 pp com significância"* que virou **empate exato** ao
dobrar a amostra. Custo estimado: ~4,3 h.

## Previsão

**Ponto entre −1,5 e 0,0 pp, esperado ~−0,7.** O IC deve ficar mais estreito que
o da R1, porque cada réplica carrega 45% mais partidas.

## Tabela de falsificação

| resultado | leitura |
|---|---|
| ponto em [−1,5; −0,2] e IC não cruza zero | **replicou.** O prior custa um pouco; a §6 leva os dois números |
| ponto negativo, IC cruza zero | replicou em **sinal**, não em significância. A frase que se sustenta é *"o prior não vale nada no agente de hoje"* |
| ponto em [0; +1] | **não replicou.** O prior é **inerte** — e a §6 leva isso, que já basta |
| ponto ≥ +5 pp | **a R1 estava errada.** Não tocar em documento nenhum antes de entender o quê |

## ⚠ O que a réplica NÃO está decidindo

**Os +10,11 pp já estão mortos, e não é esta rodada que os mata.** Nenhuma das
duas medições de 01/09 chega perto deles: a R1 deu −0,71 pp e o `sem_prior`
saltou de 38,0% (12/08) para 55,81% (01/09). A réplica decide entre **"inerte"**
e **"custa um pouco"** — não entre *"vale dez pontos"* e *"não vale"*.

Escrever isto antes importa porque, saia o que sair, a correção no relatório
acontece. O que muda é só a palavra.

## Regra de parada, declarada antes

A R2 morreu por causa externa na 7ª de 10 réplicas. **Se esta rodada não chegar
às 10 réplicas, o parcial não vale como resultado** — vira registro histórico,
como o da R2, e não se combina com nenhuma rodada posterior.

---

# R1b — **morta na 4ª réplica.** Sem resultado, e o parcial aponta para o outro lado

> 02/09. 73 min, `logs/r1b_prior_replica.log`. Pela regra de parada escrita no
> pré-registro **antes** da rodada, isto **não é resultado** — é registro.

**3 pares completos** (a 4ª réplica morreu no meio):

| par | `atual` | `sem_prior` | Δ |
|---:|---:|---:|---:|
| 1 | 55,90% | 55,70% | +0,20 |
| 2 | 55,00% | 54,90% | +0,10 |
| 3 | 55,60% | 55,10% | +0,50 |

Média: **+0,27 pp** — **sinal oposto ao da R1** (−0,71 pp).

## O que isso significa, e sobretudo o que não significa

**Não significa que a R1 estava errada.** Três pares não decidem nada: a
dispersão típica entre réplicas é **0,725 pp**, e o intervalo de três pontos
cobre confortavelmente os dois sinais.

**Significa que a réplica era mesmo necessária, e que eu não devia ter escrito
que ela provavelmente confirmaria.** O efeito da R1 (−0,71 pp) é **menor que a
resolução declarada da bancada** (0,91 pp com 10 réplicas) — eu registrei isso
no próprio resultado da R1 e depois falei como se o número estivesse firme.
Os três primeiros pares são o lembrete barato de que não está.

## A leitura que sobrevive às duas rodadas

O que **nenhuma** medição de 01–02/09 encontra é qualquer coisa parecida com
**+10,11 pp**:

| medição | régua | resultado |
|---|---|---:|
| 12/08 | painel, deck v6, pré-T6 | +10,11 pp |
| R1 (01/09) | réplicas, v9, pós-T13 | −0,71 pp |
| R1b parcial (02/09) | réplicas, v9, n=1600 | +0,27 pp (3 pares) |

**As duas medições de hoje estão dentro de ±1 pp de zero, e o número publicado
está a dez pontos de distância.** A correção no relatório não depende de qual
dos dois sinais vence — depende só de que **os dois estão em zero**. Foi
exatamente isto que o pré-registro da R1b antecipou ao declarar que a réplica
decide entre *"inerte"* e *"custa um pouco"*, não entre *"vale dez pontos"* e
*"não vale"*.

**Estado: o prior está sem número.** Para publicar *"inerte"* com a régua da
casa faltam 10 réplicas que cheguem ao fim.

## R1b — segunda tentativa, lançada em 03/09

Mesmo comando, mesmo pré-registro, **log novo** (`logs/r1b_prior_replica_2.log`)
para que o parcial de 3 pares acima continue auditável.

**Declarado antes:** o parcial da primeira tentativa **não se combina** com esta
rodada. Se esta também não chegar às 10 réplicas, também não vira resultado.

Estado da máquina ao lançar: 0 processos Python, **2,4 GB de RAM livre** de 15,3
(Opera com 8,2 GB). Anotado porque duas rodadas morreram sem causa identificada
e a memória apertada é o único fator ambiental que eu medi — **sem evidência de
que seja a causa**: não houve OOM, crash do Python, evento de erro no System nem
uso de pagefile acima de 1,9 GB de 16 GB alocados.

### Segunda tentativa: morta na 4ª réplica, 97 min. **3 de 4 rodadas mortas**

| par | `atual` | `sem_prior` | Δ |
|---:|---:|---:|---:|
| 1 | 54,80% | 55,80% | −1,00 |
| 2 | 54,90% | 55,30% | −0,40 |
| 3 | 54,80% | 55,80% | −1,00 |

Média **−0,80 pp** — desta vez **do mesmo lado da R1**.

⚠ **E isto não confirma nada.** Pela regra escrita antes de as duas tentativas
começarem, parcial não é resultado e **não se combina**. Dois parciais de três
pares que discordam entre si (+0,27 e −0,80) são a definição do ruído que a
bancada tem: dispersão típica de 0,725 pp por réplica. Se eu somasse os dois
porque o segundo é o que eu esperava, estaria escolhendo o caminho na
bifurcação — e este projeto tem onze réguas quebradas no currículo por menos.

---

# A frente de bancada FECHA — sem a réplica, e com o que basta

**3 de 4 rodadas morreram sem causa identificada.** Não há OOM, crash do
Python, evento de erro no System, reboot, nem uso de pagefile acima de 1,9 GB de
16 GB alocados. A R1 voltou como `exit code 0`; as outras três como `killed`,
que é o status de tarefa **parada**, não de tarefa que falhou. **Sem causa, sem
conserto — e insistir custa 4,3 h por tentativa.**

## O que está medido, e com que régua

| medição | régua | pares | resultado | vale? |
|---|---|---:|---:|---|
| 12/08 | painel (aposentado em 22/08), deck v6, pré-T6 | — | **+10,11 pp** | ⚠ régua aposentada |
| **R1** (01/09) | réplicas, v9, n=1100 | **10** | **−0,71 pp** [−1,20; −0,22] | **sim — rodada completa** |
| R1b-1 (02/09) | réplicas, v9, n=1600 | 3 | +0,27 pp | não |
| R1b-2 (03/09) | réplicas, v9, n=1600 | 3 | −0,80 pp | não |

## A conclusão que não depende da réplica

**As três medições com a régua corrente ficam entre −0,80 e +0,27 pp. O número
publicado está a dez pontos de todas elas.**

A correção do relatório nunca dependeu de resolver *"inerte"* contra *"custa um
pouco"* — isso estava escrito no pré-registro da R1b, **antes** de qualquer uma
das duas tentativas. Depende só de que **todas as medições de hoje estão em
zero**, e três estão.

### O que o relatório pode afirmar, e o que não pode

| pode | não pode |
|---|---|
| *"remedido com a régua corrente, o efeito fica dentro de ±1 pp de zero em três medições"* | *"o prior custa 0,71 pp"* — uma rodada completa, réplica interrompida duas vezes |
| *"os +10,11 pp valem para o agente de 12/08, com o deck v6 e a escada pré-T6"* | *"o prior é dano"* |
| *"quem mudou o veredito foi o T6, que já invertera o termo de dano na direção oposta"* | qualquer coisa que precise da réplica que não existe |

**A limitação entra declarada:** o número novo tem **uma** rodada completa, e as
duas tentativas de réplica foram interrompidas por causa que não identificamos.
Num projeto cuja regra nº 3 é *replicar antes de adotar*, isso se escreve — não
se esconde. E não há adoção: o agente está congelado desde 16/08.
