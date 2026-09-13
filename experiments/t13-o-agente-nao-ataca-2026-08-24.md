> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

> ### ⚠ Retratação parcial — 26/08: o número de divergência acima não se lê
>
> A justificativa "muda **20,9%** das decisões, acima do limiar" foi medida com
> uma régua quebrada. Rodado o controle que faltava, **duas chamadas idênticas
> do agente já discordam em ~18%** das decisões: a determinização sorteia a cada
> chamada, e a busca do engine tem aleatoriedade própria que nem `random.seed()`
> alcança. **20,9% está dentro da faixa do ruído.**
>
> **O resultado deste teste não muda** — ele foi decidido pelo painel, por
> vitória, com intervalo de confiança. O que cai é a justificativa barata que eu
> dava para gastar a bancada. Detalhe em
> [`t15`](t15-o-dano-de-novo-2026-08-26.md#-fui-medir-a-divergência-antes-do-painel-e-a-régua-quebrou-na-mão).

# T13 — o agente dança em vez de atacar: **pré-registro**

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção no fim, **sem
> editar nada acima dela**.
>
> Nasce da pergunta do Fernando: *"onde estão as jogadas erradas que fazem eu
> estar tão ruim na ladder?"*

---

## A resposta, e ela é medível

Comparando **nas mesmas posições** — decisões reais de pilotos ≥ 1.000 do nosso
próprio arquétipo, com o agente completo rodando em cima delas
([`divergencia_do_agente.py`](../../tools/divergencia_do_agente.py)):

| tipo de jogada | **eles** | **nós** | razão |
|---|---:|---:|---:|
| PLAY | 42,6% | 46,2% | 1,08× |
| CARD | 22,0% | 22,0% | 1,00× |
| ATTACH | 12,3% | 10,1% | 0,82× |
| **ATTACK** | **12,1%** | **4,8%** | **0,39×** |
| END | 4,4% | 1,9% | 0,42× |
| **RETREAT** | **3,7%** | **11,6%** | **3,18×** |
| ABILITY | 1,9% | 2,5% | 1,29× |

> **Atacamos 2,5× menos e recuamos 3,2× mais.** Mesmas posições, mesmo baralho,
> mesmas opções na mesa.

---

## O mecanismo está numa linha

```python
s += _hp_efetivo(meu_ativo) * W_HP
```

A avaliação conta a vida **do ativo** e mais nada. Recuar um Ogerpon machucado e
promover um inteiro **não cura ninguém** — mas a nota da vida salta de 60 para
210, e a avaliação paga **+150**. Descontando as energias que ficam para trás
(5 × 15), o saldo ainda é **+75**.

**São cinco energias anexadas, de graça, sem causar dano nenhum.**

E atacar, na mesma avaliação, vale **zero** a menos que nocauteie — o `W_DANO`
está em 0 **de propósito**, porque premiar dano parcial mediu −11,46 e −7,37 pp.

> O agente não está jogando mal por acidente. **Ele está fazendo exatamente o
> que o objetivo manda:** girar Pokémon para manter vida alta no ativo, porque
> isso pontua e atacar não.

---

## A intervenção

`PTCG_HP_INVARIANTE=1`: em vez de premiar a vida do ativo, **penaliza o dano
acumulado em todo o campo**.

| | por que |
|---|---|
| dano **não se move** com o recuo | trocar de ativo não cura — o termo passa a ser **invariante à rotação** |
| um Pokémon novo no banco contribui **zero** | não cria a distorção oposta, de encher o banco virar recompensa |

**Padrão desligado.** O agente embarcado não muda enquanto o teste não decidir.

### ⚠ O preço, e ele é declarado antes

O termo novo é invariante a **qual** Pokémon está no ativo — **inclusive quando
isso importa**. Depois de um nocaute é preciso promover alguém, e hoje a
avaliação prefere o inteiro (+150). Com a mudança, promover o machucado ou o
inteiro fica **neutro**.

**O que sobra para distinguir os dois é o termo de ameaça**, que penaliza o
estado em que o nosso ativo morre no turno seguinte. Pode não bastar.

**Não existe versão sem esse preço:** a avaliação julga **estados**, não ações,
e um estado depois de recuar é indistinguível de um estado depois de promover.

---

## Quanto isto muda o comportamento — medido ANTES do painel

| | |
|---|---:|
| decisões nossas comparadas | 3.778 |
| **a escolha muda em** | **788 — 20,9%** |
| RETREAT, nas posições deles | 11,6% → **7,1%** (razão 3,18× → **1,95×**) |
| ATTACK, nas posições deles | 4,8% → **5,2%** (razão 0,39× → **0,43×**) |

**Corta o excesso de recuo pela metade e quase não move o ataque.** É meia
correção, e está declarado: **o déficit de ataque tem outra causa** — o `W_DANO`
em zero — que este teste **não** toca.

Referência: o T10 mudava 23,5% das decisões e passou; a P1 mudava 0,5% e foi
retirada antes do painel.

---

## A previsão, registrada antes

> **Entre −0,8 e +1,2 pp.** Faixa cruzando zero, de propósito.

**Fundamento do lado positivo:** o termo atual paga por uma jogada que não faz
nada, e 20,9% das decisões mudam. Aproximar o comportamento de pilotos ≥ 1.000
numa dimensão medida é a melhor pista que o projeto tem.

**Fundamento do lado negativo:** a mudança **remove um sinal de sobrevivência**
sem colocar outro no lugar para a promoção pós-nocaute. Se o termo de ameaça não
cobrir esse buraco, o agente passa a promover mal — e promover mal, num deck de
um atacante só que dá 2 prêmios, é caro.

**Contra a previsão pesa o histórico:** 20+ hipóteses, 5 aprovadas; e a minha
previsão errou 3 das últimas 4.

| observação | leitura |
|---|---|
| **IC inteiro acima de zero** | o termo de vida estava pagando por dança; adotar |
| **empate** | a distorção existe e custa menos que 0,9 pp — fica registrada, não adotada |
| **IC inteiro abaixo de zero** | o sinal de sobrevivência valia mais que a distorção custava. **O próximo teste seria a promoção pós-nocaute**, não o recuo |

**Protocolo:** `comparar_decks.py --variante-a atual --variante-b t13_hp_invariante --a decks/ogerpon_v9.csv --replicas 10 --n 1100`. Família de 1. Gate conjuntivo. ~3,6 h.

---

## O que este documento NÃO afirma

1. **Divergir de um piloto forte não é erro por si só.** É o melhor proxy
   disponível, não um veredito. A bancada decide.
2. **A tabela de distribuição vem de posições DELES**, não das nossas. Mede o
   que o agente faria no lugar deles.
3. **Isto não explica a nota da ladder sozinho.** Explica uma diferença de
   comportamento grande e mecânica; quanto dela vira rating, ninguém mediu.

---

## Resultado — **PASSA**, e a previsão acertou

10 réplicas alternadas, 197 minutos, mesmo deck dos dois lados:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 54,40% | ± 0,78 pp |
| **`t13_hp_invariante`** | **55,26%** | ± 0,61 pp |

| | |
|---|---|
| diferença | **+0,86 pp** (erro padrão 0,31; Welch, 17,0 g.l.) |
| IC 95% | **[+0,20; +1,52]** — não cruza zero |
| **gate conjuntivo** | **PASSA** — nenhuma casa regride |

**A previsão registrada era −0,8 a +1,2 pp.** Deu **+0,86** — dentro da faixa, e
do lado positivo dela.

### Por casa — sobe em todas, e nenhuma regride

| casa | `atual` | `t13` | ganho | IC 95% |
|---|---:|---:|---:|---|
| ref950+Lucario 0,05 s | 35,90% | 36,98% | +1,08 | [−0,16; +2,32] |
| **ref950+Lucario 0,5 s** | 35,45% | **36,49%** | **+1,04** | **[+0,10; +1,97]** |
| ref950+sample | 70,73% | 71,88% | +1,15 | [−0,28; +2,59] |
| primeira (piso) | 75,51% | 75,68% | +0,17 | [−1,53; +1,19] |

**O preço declarado não se materializou.** Eu havia registrado que tornar a
promoção pós-nocaute neutra podia custar caro, e que se desse negativo o próximo
teste seria a promoção. Não deu: o termo de ameaça parece bastar.

---

## O padrão que já são três

Este é o **terceiro** teste aprovado cuja causa é a mesma:

| # | a avaliação pagava por... | efeito |
|---|---|---:|
| **T6** | atacar e passar o turno estarem enterrados na escada | +1,03 pp |
| **T10** | energia no banco valer o mesmo que no ativo | +0,88 pp |
| **T13** | vida do ativo subir quando se troca de Pokémon | **+0,86 pp** |

**Nos três, o agente estava otimizando algo que não é progresso.** Não era falta
de busca, nem de dados, nem de profundidade — era o objetivo estar errado em
lugares específicos e identificáveis.

E os três foram encontrados do mesmo jeito: **comparando o comportamento com
pilotos fortes do mesmo baralho**, não olhando o código.

---

## ⚠ NÃO ADOTADO AINDA — falta a réplica

A Parte 1.1 do protocolo exige **replicar com configuração diferente**. Esta é
uma medição.

### A réplica, pré-registrada agora

Há **duas** formas de tornar o termo invariante ao recuo, e elas **não** são a
mesma coisa:

| forma | fórmula | efeito colateral |
|---|---|---|
| **a testada** | `s −= dano_total_do_campo × W_HP` | Pokémon novo no banco contribui **zero** |
| **a alternativa** | `s += vida_total_do_campo × W_HP` | Pokémon novo no banco contribui **+210** — recompensa encher o banco |

`−Σdano = −Σ maxHp + Σ hp`, e **`Σ maxHp` muda quando alguém entra ou sai do
campo** — então as duas fórmulas divergem exatamente na dimensão "quantos
Pokémon estão em jogo".

`PTCG_HP_INVARIANTE=2` liga a segunda.

**Previsão registrada:** *a variante `2` também ganha, entre +0,2 e +1,2 pp.*
Fundamento: o que corrige a distorção é a **invariância à rotação**, que as duas
têm. Contra: a segunda paga 210 por Pokémon no banco, contra os 8 do `W_BANCO` —
uma distorção nova, 26× maior que o termo que já existia para isso.

| observação | leitura |
|---|---|
| **as duas ganham parecido** | é a **invariância**, não a fórmula — e a distorção de banco não custa o bastante para aparecer |
| **só a `1` ganha** | a fórmula importa: pagar por Pokémon no campo custa o que a invariância rende |
| **a `2` ganha mais** | subestimei o valor de desenvolver o banco |
| nenhuma ganha | o +0,86 do T13 era ruído; o gate teve sorte |

---

## Resultado da réplica — **NÃO replicou**, e a minha previsão errou

10 réplicas alternadas, 201 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | **54,76%** | ± 0,97 pp |
| `t13b_vida_do_campo` | 54,02% | ± 0,87 pp |

| | |
|---|---|
| diferença | **+0,74 pp a favor do `atual`** (erro padrão 0,41; Welch, 17,8 g.l.) |
| IC 95% | **[−0,12; +1,60]** |
| veredito | **empate estatístico** — e o ponto estimado é **contra** a forma 2 |

**A previsão registrada era "a forma 2 também ganha, entre +0,2 e +1,2 pp".**
Errei o **sinal**: ela não ganhou, e o ponto aponta para o outro lado.

---

## O que isto quer dizer, e o que **não** quer

Pela tabela escrita antes de medir:

> **só a `1` ganha** → a fórmula importa: pagar por Pokémon no campo custa o que
> a invariância rende

**É isso.** As duas formas são igualmente invariantes ao recuo, e só uma ganha.
Então **não é a invariância sozinha** que corrige — é a invariância **sem** pagar
por ter mais Pokémon em campo.

A forma 2 paga **210 por Pokémon no banco**, contra os **8** do `W_BANCO`. Ela
conserta a distorção do recuo e instala uma **26× maior** no lugar.

### É o padrão do T6 ao contrário, e vale registrar

| | T6 | **T13** |
|---|---|---|
| desenho | dois valores da mesma mudança | **duas fórmulas** da mesma ideia |
| resultado | os dois renderam igual | **só uma rende** |
| leitura | a explicação (**magnitude**) caiu; sobrou a **ordem** | a explicação (**invariância**) **não basta**; a fórmula importa |

No T6 o controle **derrubou** a minha explicação. Aqui ele **restringiu** a
explicação, sem derrubá-la: a invariância continua sendo necessária — só não é
suficiente.

---

## ⚠ O T13 continua **NÃO ADOTADO**, e agora por um motivo melhor

O que o T13b **não** diz: que os +0,86 pp da forma 1 eram ruído. Ele testou uma
**intervenção diferente**, não a mesma noutra configuração — o precedente do T9
trocou o *preenchimento* mantendo o *corte*, e aqui a forma 2 muda o mecanismo.

**Falta a réplica de verdade:** a forma 1, com configuração diferente.

### A réplica, pré-registrada agora

`PTCG_W_HP=0.5` com `PTCG_HP_INVARIANTE=1` — a **mesma fórmula**, com o peso do
termo pela **metade**.

| observação | leitura |
|---|---|
| **ganha parecido (+0,3 a +1,3)** | o que corrige é **remover o bônus de rotação**, e o peso é secundário. **Adotar** |
| **ganha bem menos** | o valor está no **peso**, não na invariância — e aí o T13 vira ajuste de parâmetro, que este projeto não faz sem medir a curva |
| **empata** | os +0,86 não sobrevivem a mexer no peso; o T13 não se adota |

**Previsão registrada:** *ganha, entre +0,3 e +1,3 pp.* Fundamento: o mecanismo
identificado é a rotação valer +75 de graça, e isso desaparece com qualquer peso
positivo na fórmula 1. Contra: a minha previsão errou o sinal na rodada anterior,
e o peso do termo de sobrevivência não é obviamente irrelevante.

---

## Resultado da réplica de verdade — o **ponto** replicou, a **rodada** não resolveu

10 réplicas alternadas, 196 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 54,48% | ± 0,92 pp |
| **`t13c_peso_meio`** | **55,13%** | ± 0,89 pp |

| | |
|---|---|
| diferença | **+0,65 pp** a favor do T13c (erro padrão 0,40; Welch, 18,0 g.l.) |
| IC 95% | **[−0,20; +1,50]** — cruza zero |
| veredito do tool | **empate estatístico** |

A previsão registrada era **+0,3 a +1,3 pp**. O ponto deu **+0,65** — **dentro
da faixa**. O intervalo é que não fecha.

### As duas medições da mesma fórmula

| rodada | efeito | IC 95% | o que a rodada **resolvia** |
|---|---:|---|---:|
| **T13** (`W_HP` = 1,0) | **+0,86** | [+0,21; +1,51] | 0,65 pp |
| **T13c** (`W_HP` = 0,5) | **+0,65** | [−0,19; +1,49] | **0,84 pp** |

**O T13c não falhou em replicar — falhou em resolver.** O efeito de ~0,65 pp é
menor que os 0,84 pp que esta rodada enxergava, porque a dispersão subiu (0,92 e
0,89, contra 0,78 e 0,61 no T13). Mesmo σ nominal, rodadas diferentes.

---

## ⚠ O meu pré-registro estava ambíguo, e eu não vou resolver a ambiguidade a meu favor

A tabela que escrevi **antes** de medir dizia:

| observação | leitura |
|---|---|
| **ganha parecido (+0,3 a +1,3)** | é a rotação; o peso é secundário. **Adotar** |
| **empata** | os +0,86 não sobrevivem a mexer no peso; **não se adota** |

**O resultado satisfaz as duas linhas ao mesmo tempo:** +0,65 está *dentro* da
faixa "ganha parecido", e o IC *cruza zero*, o que é "empata".

Isso é um **defeito da minha tabela**, não do resultado. Escrevi categorias que
não são mutuamente exclusivas — misturei um critério de **ponto** com um de
**intervalo** — e só percebi depois de ver o dado. **Escolher agora a linha que
me convém é exatamente o jardim de caminhos que se bifurcam.**

> **Decisão: NÃO ADOTADO.** Na dúvida entre duas leituras pré-registradas, fica
> a conservadora. O agente embarcado não muda.

### E a evidência que existe, marcada como pós-hoc

Combinando as duas medições por variância inversa — **não pré-registrado**:

| | |
|---|---|
| efeito combinado | **+0,78 pp** |
| IC 95% | **[+0,30; +1,26]** |

**Duas rodadas independentes, as duas positivas, pontos de +0,86 e +0,65.**
Isso é sugestivo e **não é um gate**: combinar depois de ver os dados é
justamente o que o pré-registro existe para evitar. Fica registrado como o que
é.

---

## O que resolve isto, e está lançado

O problema não é o efeito — é a **resolução**. Com 10 réplicas a bancada enxerga
0,65 a 0,84 pp, e o efeito mora exatamente nessa faixa.

**T13d: a mesma configuração do T13 (`W_HP` = 1,0), com 20 réplicas.**

| | 10 réplicas | **20 réplicas** |
|---|---:|---:|
| erro padrão esperado | ~0,31 | **~0,22** |
| resolve | 0,65 pp | **~0,46 pp** |
| custo | 3,6 h | **7,2 h** |

Com 0,46 pp de resolução, um efeito de 0,78 pp aparece com folga — **ou some, e
aí a resposta também é clara.**

**Previsão registrada:** *entre +0,4 e +1,2 pp, com o IC inteiro acima de zero.*

| observação | leitura |
|---|---|
| **IC acima de zero** | replicado com N que resolve. **Adotar** |
| **empate com IC estreito** (largura < 0,9) | o efeito é menor que 0,4 pp; **não se adota**, e a distorção fica registrada como real e barata |
| **negativo** | as duas rodadas anteriores foram sorte; o T13 morre |

**Desta vez as três linhas são mutuamente exclusivas**, e a do meio tem critério
numérico. Foi o que faltou na tabela anterior.

---

## Resultado decisivo — **PASSA**, e a previsão acertou as duas metades

20 réplicas alternadas, 393 minutos:

| | vitórias | dispersão |
|---|---:|---:|
| `atual` | 54,70% | ± 0,80 pp |
| **`t13_hp_invariante`** | **55,29%** | ± 0,76 pp |

| | |
|---|---|
| diferença | **+0,59 pp** (erro padrão **0,25**; Welch, **37,9 g.l.**) |
| IC 95% | **[+0,09; +1,09]** — não cruza zero |
| **gate conjuntivo** | **PASSA** — nenhuma casa regride |

**A previsão registrada era "+0,4 a +1,2 pp, com o IC inteiro acima de zero".**
Deu **+0,59 com IC [+0,09; +1,09]** — **ponto e veredito, os dois certos.**

Pela tabela pré-registrada: *"IC acima de zero → replicado com N que resolve.
**Adotar**"*.

> ## ✅ ADOTADO — `PTCG_HP_INVARIANTE = 1`

---

## As três medições, e o que elas ensinam sobre a primeira

| rodada | réplicas | efeito | IC 95% |
|---|---:|---:|---|
| T13 | 10 | **+0,86** | [+0,21; +1,51] |
| T13c (peso 0,5) | 10 | +0,65 | [−0,20; +1,50] |
| **T13d** | **20** | **+0,59** | **[+0,09; +1,09]** |

**O ponto estimado caiu conforme o N subiu: 0,86 → 0,65 → 0,59.**

Isso é a **maldição do vencedor**, e é esperado: a primeira medição que cruza o
limiar de significância tende a superestimar o efeito, porque é justamente o
ruído favorável que a empurrou para cima do limiar. O valor honesto para citar é
o de **maior N: +0,59 pp**, não o primeiro que apareceu.

**Vale como regra:** quando um efeito passa raspando com 10 réplicas, o número
a publicar é o da rodada maior — não a média, e nunca o maior dos três.

---

## O placar do projeto, atualizado

| # | mudança | efeito | tipo |
|---|---|---:|---|
| — | Tera Orb 2 → 4 | +2,24 pp | lista |
| T9 | Night Stretcher 3 → 1 | +1,09 pp | lista |
| T1 | Lively Stadium | +1,04 pp | lista |
| **T6** | compressão de `ATTACK`/`END` | +1,03 pp | **objetivo** |
| **T10** | energia do banco vale zero | +0,88 pp | **objetivo** |
| **T13** | vida deixa de pagar por rotação | **+0,59 pp** | **objetivo** |
| T8 | Hero's Cape | +0,19 pp | **adotada contra o gate** |

**Seis aprovações no gate, uma adoção contra ele.** E **três das seis** têm a
mesma causa: a avaliação premiava algo que não é progresso.
