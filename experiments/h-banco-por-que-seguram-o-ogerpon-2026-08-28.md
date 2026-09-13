> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entra numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# H-banco — por que os pilotos fortes seguram o Ogerpon: **pré-registro**

> **Categoria C** — diagnóstico observacional. **Não é teste de bancada**: não
> há A/B, não há gate, e nada aqui adota nada. O produto é **um gatilho ou a
> morte da pergunta**.
>
> ⚠ **ESCRITO ANTES DE MEDIR.**

---

## A pergunta, e por que ela sobrou

Em turnos onde baixar Ogerpon é jogada legal:

| | taxa |
|---|---:|
| **o nosso agente baixa** | **97,7%** [93,5; 99,2] |
| **pilotos ≥ 1.000 do mesmo arquétipo baixam** | **~21,3%** [15; 29] |

**4,6×** — a maior divergência de comportamento do projeto, maior que o déficit
de ataque (2,5×). Depois que o [T16](t16-o-que-o-nocaute-destroi-2026-08-26.md)
fechou a fila de termos de avaliação, é a **única** frente aberta no agente que
não passa por mais busca — e a busca já reprovou cinco vezes.

**A explicação óbvia já foi falsificada** em 19/08: se a disciplina fosse *"não
encha o banco de `ex` de dois prêmios"*, a taxa cairia conforme cópias em campo.
Medida, ela é **plana e se inclina para cima** (18,8% → 19,7% → 22,5% → 26,3%).

---

## O primeiro suspeito é o instrumento, e por isso o controle vem antes

**Régua nova nasce com controle** (regra nº 8), e o projeto já quebrou **dez**
réguas em vinte dias — cinco delas apareceram como número incoerente, exatamente
como este 4,6×.

Duas coisas, porém, já estão a favor da medição estar certa:

1. **Os dois lados contam por TURNO**, não por decisão — o erro que fez o Teal
   Dance parecer 34% quando roda 90,6% (régua quebrada nº 6). O
   `treinadores_segurados.py` e o `auditoria_de_turno.py` acumulam dentro do
   turno e só fecham quando o turno vira.
2. **Os dois usam a lista de opções do próprio engine**, e o engine **só oferece
   jogada legal** — medido em 19/08: em 910 ofertas de Apoiador, **zero**
   ocorreram com o slot do turno já gasto.

**Sobra uma diferença que nenhum dos dois documentos controlou: são populações
diferentes.** O nosso 97,7% vem do nosso agente contra o painel; o 21,3% vem da
ladder. Se a taxa baixa for propriedade **da ladder** e não **da perícia**, não
há nada a aprender com eles.

### O controle: a taxa por faixa de rating

| faixa | leitura se a taxa subir/descer | leitura se ficar plana |
|---|---|---|
| < 800 · 800–999 · 1.000–1.099 · ≥ 1.100 | segurar é **perícia**, e o gatilho existe | segurar é **população**, e a comparação com o nosso agente nunca disse o que parecia dizer |

**Previsão registrada: PLANA, dentro de ±10 pp entre a faixa mais baixa e a mais
alta.** Fundamento: no levantamento de 19/08, **nenhuma** das 14 cartas passou de
59,4% de uso por turno — nem Pokégear, nem Jumbo Ice Cream. "Segurar quase tudo"
tem cara de propriedade do campo inteiro, não de disciplina de quem ganha.

**E eu registro que estou prevendo contra o meu próprio interesse:** se a taxa
for plana, a maior divergência aberta do projeto vira um artefato de comparação,
e não sobra frente nenhuma no agente.

---

## As quatro hipóteses de gatilho, com o mecanismo antes do número

Todas medidas **na mesma passada**, com a unidade turno e IC de Wilson.

| # | gatilho | mecanismo | previsão registrada |
|---|---|---|---|
| **H1** | **{G} básica na mão** | baixar um Ogerpon **sem** energia para alimentá-lo não liga o Teal Dance e entrega 2 prêmios. Com {G} na mão, o segundo Ogerpon **paga no mesmo turno** | **≥ 20 pp** a favor de "com {G}" |
| **H2** | **prêmios dele** | quando ele fecha a partida com 1 nocaute, pôr mais um `ex` de 2 prêmios no banco é entregar a corrida | queda de **≥ 15 pp** entre 6 e 2 prêmios restantes |
| **H3** | **arquétipo do adversário** | contra quem castiga o banco (Dragapult ex, 18,8% do campo), banco cheio é dano de graça | **≥ 10 pp** abaixo do resto do campo |
| **H4** | **turno da partida** | cedo é montagem, tarde é execução — depois de montado, o Ogerpon extra só entrega prêmio | queda monotônica com o turno |

**H1 é a favorita, e o motivo é que ela é a única com mecanismo que o nosso
agente pode executar:** a avaliação sabe quantas {G} há na mão. As outras três
descrevem o lado dele — e o placar do projeto para termos que descrevem o lado
dele é **0 aprovados de 6** ([T16](t16-o-que-o-nocaute-destroi-2026-08-26.md)).

---

## A tabela de falsificação

| resultado | leitura | ação |
|---|---|---|
| **controle de rating não é plano** e algum gatilho separa | há perícia e há mecanismo | pré-registrar um teste de bancada com a regra escrita **antes** |
| **controle plano**, gatilhos separam mesmo assim | não é perícia, mas há estrutura no jogo | registrar; **não** virar regra sem mecanismo causal |
| **controle plano e tudo plano** | a divergência é artefato de população | **fechar a pergunta**, e o agente fica sem frente aberta — que é um resultado, não um fracasso |
| **algum gatilho separa acima de 30 pp** | forte demais para diagnóstico observacional | desconfiar do instrumento **primeiro**: procurar o confundidor antes de comemorar |

---

## O que este diagnóstico NÃO pode fazer

1. **Não adota nada.** Mesmo um gatilho limpo só vira mudança depois de um teste
   de bancada com 20 réplicas (~6,4 h) e do gate conjuntivo.
2. **É observacional.** Nada foi sorteado: mão pequena também significa turno
   tardio, banco montado e energia já anexada. As tabelas separam por covariável,
   mas isso **não** elimina confundimento.
3. **Cobertura de identificação de carta ~75%** — o `_carta_da_opcao` não resolve
   todas as opções, e o resto fica fora da conta.
4. **Não mede o que teria acontecido.** Uma taxa diz o que fizeram, nunca se
   estavam certos. O contrafactual exige bancada.

---

## O protocolo

```
python tools/gatilho_do_banco.py --n 2800
```

**2.800 episódios locais** (09/08 a 22/08), todos os lados do arquétipo
`Teal Mask Ogerpon ex` com rating conhecido — **sem corte de rating**, porque a
faixa de rating **é** o controle. Unidade: turno. IC de Wilson.

---

## Resultado — **o controle foi plano, e a réplica encontrou algo maior**

2.800 episódios (09 a 22/08), **244 turnos** com a oferta de baixar o Ogerpon.

**Primeiro, o instrumento se confirma.** Taxa agregada **22,1%** [17,4; 27,7],
contra os **21,3%** [15; 29] medidos em 19/08 por outra ferramenta, com 1,5× mais
episódios. **A régua não está quebrada** — a divergência de comportamento é real.

### O controle: **plano**, como a previsão registrada dizia

| faixa de rating | baixou | turnos | taxa |
|---|---:|---:|---:|
| 800–999 | 32 | 142 | **22,5%** [16,4; 30,1] |
| ≥ 1.000 | 22 | 102 | **21,6%** [13,6; 29,4] |

**−1,0 pp, IC 95% [−11,5; +9,6].** A previsão registrada era *plana dentro de
±10 pp* — **acertou**, e ela era contra o meu próprio interesse.

> **Segurar o Ogerpon não é perícia.** Quem joga em 850 segura tanto quanto quem
> joga em 1.050. A leitura *"os pilotos fortes sabem algo que o nosso agente não
> sabe"* **perde a base**: o que existe é uma propriedade da população da ladder,
> não um sinal de habilidade.

**Limite declarado do controle:** o índice de ratings só cobre **800–1.100**.
"Plano" vale nesse intervalo. Não há dado abaixo de 800 para testar o extremo.

### As quatro hipóteses

| # | gatilho | efeito de ligar | IC 95% | Bonferroni(4) |
|---|---|---:|---|---|
| H1 | com {G} contra sem {G} | +8,4 pp | [−1,9; +18,7] | não exclui |
| H1b | ≥ 2 {G} contra 0 | +14,9 pp | [+0,9; +28,9] | **não exclui** |
| H2 | prêmios dele ≤ 4 | **−18,9 pp** | [−28,5; −9,4] | exclui |
| **H3** | **adversário é Dragapult ex** | **−19,3 pp** | [−29,7; −9,0] | **exclui** |
| H4 | turno ≥ 9 | **−17,8 pp** | [−27,8; −7,8] | exclui |

**H1 não passa no tamanho que eu declarei.** A previsão era **≥ 20 pp** e deu
+8,4. O extremo (≥ 2 {G} contra nenhuma) chega a +14,9 e exclui zero no IC de
95%, mas **morre sob Bonferroni(4)** — que é a regra da casa, declarada antes.
A direção é a prevista e a magnitude não é. **Não estabelecida.**

**H2 e H4 são o mesmo eixo, e isso está medido, não suposto.** Prêmio cai
conforme o turno passa, e cada um **morre** quando controlado pelo outro:

| | efeito | IC 95% |
|---|---:|---|
| H4 dentro de 6 prêmios (jogo ainda 0×0) | −12,7 pp | [−39,4; +14,0] |
| H2 dentro de turnos ≤ 8 | −17,4 pp | [−31,6; −3,3] — e some sob Bonferroni |

Um eixo só: **fim de jogo**. Registrado como um, não como dois.

### H3 é a única que sobrevive aos dois controles

| recorte | Dragapult | resto | efeito |
|---|---:|---:|---:|
| tudo | 4,5% (1/22) | 23,9% (53/222) | **−19,3 pp** |
| só turnos ≤ 8 | 4,8% (1/21) | 27,5% (50/182) | **−22,7 pp** [−33,9; −11,5] |
| só com 6 prêmios dele | 5,0% (1/20) | 29,1% (48/165) | **−24,1 pp** [−35,9; −12,3] |

Turno mediano contra Dragapult **4,5**, contra o resto **4,0** — não é lentidão
disfarçada. E o mecanismo estava escrito **antes**: o Dragapult castiga o banco
com dano espalhado, então banco cheio de `ex` de dois prêmios é dano de graça.

**Mas n = 22, e é 1 turno de 22.** Pela regra da casa isso não decide nada
sozinho: pede réplica fora da amostra.

---

## ⚠ A réplica não pôde ser feita — e o motivo é o achado principal

Baixei os cinco dias que faltavam (23 a 27/08, **1.000 episódios novos**) para
replicar o H3 fora da amostra. Rendimento: **4 turnos**, contra os ~90 que a
proporção da primeira passada previa.

Não é a ferramenta. **É que o nosso arquétipo desapareceu da ladder.**

| dia | lados amostrados | Teal Mask Ogerpon ex |
|---|---:|---:|
| 09/08 | 400 | **5,2%** [3,5; 7,9] |
| 14/08 | 400 | 2,0% [1,0; 3,9] |
| 19/08 | 400 | 1,0% [0,4; 2,5] |
| **20, 22, 25 e 27/08** | **1.600** | **0,0%** [0,00; 0,24] |

**Zero em 1.600 lados.** O intervalo superior é **0,24%** — não é amostragem
azarada, é ausência.

E o campo que ficou no lugar:

| arquétipo | 14/08 | **27/08** |
|---|---:|---:|
| **Dragapult ex** | 27,5% | **34,5%** |
| **Mega Kangaskhan ex** | — | **24,2%** |
| Hydrapple ex | 10,5% | 21,0% |
| **Marnie's Grimmsnarl ex** | 16,0% | **fora do top 6** |

---

## O que isto fecha, e o que ele custa admitir

**1. A pergunta original está respondida, e a resposta é "não há o que copiar".**
O controle é plano: segurar não é perícia. E a população que segurava **não joga
mais este baralho**. A comparação "nós × pilotos ≥ 1.000 do mesmo arquétipo"
descreve um campo que deixou de existir — **é a lição do T15 aplicada ao
adversário em vez de ao agente**: uma medição vale para o estado em que foi
feita, e o estado aqui inclui **quem está do outro lado da mesa**.

**2. O H3 fica registrado como hipótese viva e não replicável.** Não é possível
gerar mais dado: ninguém mais pilota o arquétipo. E mesmo que fosse verdade, o
painel **não tem Dragapult** — ele é Lucario ref950, sample e piso, e as casas de
meta já foram medidas duas vezes como não-funcionais (o nosso agente com deck
alheio vale 0,7 pp sobre a política nula). **Um gatilho que a bancada não
consegue instanciar não é uma frente de trabalho, é uma nota de rodapé.**

**3. As duas premissas do deck que ainda apareciam na documentação morreram por
completo.** A justificativa original — *"o dominante do campo, 34%, é fraco ao
nosso tipo"* — perdeu o dominante: o Grimmsnarl saiu do top 6. E o
**Mega Kangaskhan ex**, registrado como **o nosso pior confronto** (bate 350 e
nos nocauteia de um golpe, enquanto precisa de 3 nocautes), é hoje **um quarto do
campo**.

**4. E isso vale para o relatório, não para o agente.** O gate deste projeto foi
julgado contra o Lucario, **3,1% do campo**; a lista foi construída contra um
campo de 14/08 que já não existe; e a única submissão possível fechou em 16/08.
**Nada disto é acionável no agente.** É, porém, a terceira demonstração empírica
da tese que organiza o writeup — a qualidade não é propriedade do agente, é
propriedade do par — com um agravante que o texto ainda não diz: **o par também
deriva no tempo.**

---

## Veredito

Pela tabela de falsificação escrita antes: *"controle plano, gatilhos separam
mesmo assim → não é perícia, mas há estrutura no jogo → registrar; **não** virar
regra sem mecanismo causal"*.

**Registrado. Não vira regra. A pergunta fecha** — e fecha por dois motivos
independentes, um estatístico (o controle) e um material (a população sumiu).

**A fila do agente está vazia nas duas pontas:** sem termo de avaliação
([T16](t16-o-que-o-nocaute-destroi-2026-08-26.md)) e sem gatilho de política.
O que resta do projeto é o relatório.

---

# ⚠ RETRATAÇÃO, no mesmo dia — a régua quebrada nº 11 é minha

> **Tudo o que está acima do traço foi medido com o filtro errado.** O veredito
> final não muda; **os números e três das quatro conclusões mudam**, e uma delas
> inverte de sinal. O texto acima fica **inalterado**, como manda a convenção do
> projeto: retratação é bloco marcado, nunca edição silenciosa.

## O erro

A pergunta é sobre a decisão de **baixar a carta 96**. O filtro selecionava
lados pelo **rótulo do arquétipo** (`arquetipo == "Teal Mask Ogerpon ex"`).
Parecia a mesma coisa. Não é:

| onde a carta 96 está, no campo de 23–27/08 | lados | cópias/lado |
|---|---:|---:|
| **Hydrapple ex** | **359 de 359** | 4,0 |
| Mega Kangaskhan ex | 35 de 482 | 3,0 |
| Arboliva ex | 21 de 21 | 4,0 |
| rótulo "Teal Mask Ogerpon ex" | 2 de 2 | 4,0 |
| **total** | **417 de 2.000 = 20,8%** [19,1; 22,7] | |

**Medindo o rótulo, o campo parecia extinto (0,1%). Medindo a carta, ela está em
um lado em cada cinco.** O casco mudou; o atacante não.

Achado ao construir o mapa de ameaças do campo atual, quando o Hydrapple ex
apareceu com *"atacante dele: Teal Mask Ogerpon ex"*.

## O que isso fez com a amostra

| | turnos com a oferta |
|---|---:|
| filtro por **rótulo** (o de cima) | 244 |
| filtro pela **carta**, mesmo período | **1.745** |
| filtro pela **carta**, 23–27/08 (réplica) | **894** |

O filtro antigo via **14%** da população, e justamente a fatia atípica.

## Os números corrigidos

**A taxa base não é 22%.**

| período | turnos | taxa de baixar |
|---|---:|---:|
| 09–22/08 | 1.745 | **38,0%** [35,7; 40,3] |
| 23–27/08 (réplica) | 894 | **40,6%** [37,4; 43,9] |

Os dois períodos concordam. **A divergência com o nosso agente (97,7%) é real,
mas é 2,4× — não 4,6×.**

### O que decide é o CASCO, e não é gatilho de política

| casco de quem decide | taxa | turnos |
|---|---:|---:|
| **Hydrapple ex** | **41,2%** [38,5; 43,9] | 1.297 |
| Arboliva ex | 37,5% [28,1; 47,9] | 88 |
| Mega Kangaskhan ex | 36,5% [27,9; 46,1] | 104 |
| **Teal Mask Ogerpon puro — o nosso** | **22,1%** [17,4; 27,7] | 244 |

**+19,0 pp** [+13,2; +24,9] do Hydrapple sobre o casco puro. Os 22% de cima
existem — são a taxa **do nosso próprio casco**, que é a minoria da população e
que em 23–27/08 apareceu **4 vezes**.

### O controle de rating sobrevive, e agora com o confundidor à mostra

| contraste | efeito |
|---|---:|
| rating ≥ 1.000 contra < 1.000, **agregado** | **+8,3 pp** [+2,9; +13,6] — exclui zero |
| o mesmo, **dentro do casco Hydrapple** | +3,6 pp [−3,6; +10,8] — cruza zero |
| o mesmo, **dentro do casco Ogerpon puro** | −1,0 pp [−11,5; +9,6] — cruza zero |
| réplica 23–27/08, dentro do Hydrapple | −6,4 pp [−17,7; +4,9] — cruza zero |

**O efeito de rating era confundimento por casco:** pilotos melhores usam mais o
casco que baixa mais. Estratificado, ele some nos dois cascos e nos dois
períodos. **A conclusão original — segurar não é perícia — fica de pé, com N
sete vezes maior e com o confundidor nomeado.**

### As quatro hipóteses de gatilho: nenhuma sobrevive

| # | com o filtro errado (n=244) | com a carta (n=1.745) | veredito |
|---|---:|---|---|
| H1 · {G} na mão | +8,4 pp | 38,8% / 38,3% / 36,8% por faixa — **plano** | morre |
| H2 · prêmios dele | −18,9 pp | 37,3 / 36,8 / 36,5 / 33,1 / 43,9 / 38,5% — **plano** | morre |
| **H3 · Dragapult** | **−19,3 pp** | **+6,6 pp** [−0,3; +13,5] — **sinal invertido** | morre |
| H4 · turno | −17,8 pp | 38,6 / 39,1 / 37,5 / 32,2% — **plano** | morre |

**O H3 é o caso mais duro.** Ele sobrevivia a Bonferroni(4) e a dois controles,
com mecanismo pré-registrado — e era **1 turno de 22**. Com 416 turnos o efeito
aponta para o **outro lado** e cruza zero; na réplica, +2,9 pp [−6,0; +11,8].
**Um efeito que sobrevive a todos os controles ainda pode ser ruído se a
amostra foi selecionada errado — nenhum controle estatístico protege contra o
denominador errado.**

## O que eu afirmei hoje e está errado

| afirmei | é |
|---|---|
| *"o nosso arquétipo sumiu da ladder"* | **a nossa LISTA sumiu.** A carta está em 20,8% [19,1; 22,7] dos lados |
| *"não é possível gerar mais dado"* | **falso** — 894 turnos em 5 dias novos |
| *"o H3 é irreplicável"* | replicado, e **caiu** |
| *"a divergência é 4,6×"* | **2,4×** contra o campo; 4,4× contra o nosso próprio casco |
| *"a população deixou de existir"* | ela **trocou de casco**, o que é outra coisa e mais interessante |

## O que fica

1. **O veredito não muda: não vira regra.** Nenhum gatilho, o controle nulo.
2. **A régua quebrada nº 11 entra no livro-razão**: *medir o rótulo quando a
   pergunta é sobre a carta.* Foi encontrada em ~3 h, por um número de outra
   frente que não fechava — o mesmo padrão de cinco das dez anteriores.
3. **E sobra um achado que vale mais que a pergunta original:** o campo
   **convergiu para o nosso atacante dentro de outro casco**. Isso é matéria de
   Deck Score, e está em [`campo-atual`](../campo-atual-2026-08-28.md).
