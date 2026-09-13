> **🧪 REGISTRO DE TESTE.** Documento imutável: o pré-registro foi escrito
> **antes** de medir e o resultado entrou numa seção no fim, sem editar nada
> acima. Retratações aparecem como bloco marcado, nunca como edição silenciosa.
>
> Índice dos testes: [`testes/README`](README.md) · estado atual:
> [`CONTINUAR-AQUI`](../CONTINUAR-AQUI.md)

# T12 — os ganhos **somam**? **pré-registro**

> **Categoria C** — bancada e medições.
>
> ⚠ **ESCRITO ANTES DE MEDIR.** O resultado entra numa seção no fim, **sem
> editar nada acima dela**.

---

## A pergunta que o projeto nunca fez

Cinco alterações foram adotadas, e **cada uma foi medida sozinha**, contra o
estado que já continha as anteriores. Isso é o desenho certo — mas responde
sempre a mesma pergunta: *“esta mudança, isolada, paga?”*

**Nunca se perguntou se elas somam.** E há motivo para duvidar, ao menos entre
as duas de política:

| | o que muda |
|---|---|
| **T6** (compressão) | a **ordem dos tipos** na escada: atacar e passar o turno sobem para o meio da escala |
| **T10** (energia do banco) | a **avaliação do estado** resultante: energia no banco deixa de valer o mesmo que a do ativo |

Camadas diferentes — mas **as duas mexem em quando o agente para de jogar carta
e ataca**. Se houver sobreposição, o ganho conjunto é menor que a soma.

## O desenho

`comparar_decks.py --variante-a politica_15_08 --variante-b atual --a decks/ogerpon_v9.csv --replicas 10 --n 1100`

| variante | compressão | fração do banco |
|---|---:|---:|
| `politica_15_08` | **0,0** | **1,0** |
| `atual` | 0,5 | 0,0 |

**O deck é o mesmo dos dois lados** (`v9`), então isto mede **só a política**.
A parte de deck da diferença entre 15/08 e hoje (v6 → v9) fica de fora — e fica
declarado que fica.

**Instrumento:** `comparar_decks`, que mede por réplica e alterna A, B, A, B.
Não o painel (armadilha nº 5).

---

## A previsão, registrada antes

> **Entre +1,2 e +2,2 pp.** A soma aritmética é **+1,91** (1,03 + 0,88).

**Fundamento do centro perto da soma:** os dois agem em camadas distintas — um
na ordenação por tipo, outro na função de avaliação — e nenhum dos dois foi
medido com o outro desligado, o que já os torna parcialmente independentes por
construção.

**Fundamento do piso abaixo da soma:** as duas mudanças empurram na mesma
direção comportamental (segurar o ataque, alimentar o ativo). Sobreposição
parcial é o resultado mais provável entre os dois extremos.

**Contra a previsão:** o histórico do projeto é de efeitos menores do que o
esperado, e este é o primeiro teste de composição — não há precedente interno
para calibrar.

| observação | leitura |
|---|---|
| **+1,2 a +2,2** | previsto: os ganhos somam, com sobreposição pequena ou nenhuma |
| **acima de +2,2** | **sinergia** — o par vale mais que as partes, e isso seria novo |
| **+0,4 a +1,2** | sobreposição forte: uma das duas está fazendo boa parte do trabalho da outra |
| **abaixo de +0,4** | as duas se cancelam em boa medida, e o placar somado do projeto está inflado |

---

## O que este teste NÃO responde

1. **Não mede o deck.** A diferença total entre o que está na ladder e o que
   temos inclui `v6 → v9`, que não entra aqui.
2. **Não replica.** É uma medição; adotar não está em jogo — as duas mudanças
   já foram adotadas com réplica própria.
3. **Se der sobreposição, nada volta atrás.** Cada uma passou no gate no estado
   em que foi medida. O que muda é **como o projeto relata o placar**: somar
   ganhos medidos isoladamente passaria a exigir ressalva.

---

## Resultado — **somam, e a minha previsão ficou curta**

10 réplicas alternadas, 218 minutos, mesmo deck (`v9`) dos dois lados:

| | vitórias | dispersão |
|---|---:|---:|
| `politica_15_08` | **51,88%** | ± 0,85 pp |
| **`atual`** | **54,44%** | ± 0,46 pp |

| | |
|---|---|
| diferença | **+2,56 pp** a favor da política atual (erro padrão 0,31; Welch, 13,8 g.l.) |
| IC 95% | **[+1,90; +3,22]** |
| **gate conjuntivo** | **PASSA** |
| réplicas pareadas | **10 de 10** |

### As quatro casas melhoram, e todas com IC acima de zero

| casa | `politica_15_08` | `atual` | ganho | IC 95% |
|---|---:|---:|---:|---|
| ref950+Lucario 0,05 s | 32,01% | **35,28%** | **+3,27** | [+1,99; +4,55] |
| ref950+Lucario 0,5 s | 32,41% | **35,48%** | **+3,07** | [+1,91; +4,24] |
| ref950+sample | 69,85% | **71,96%** | **+2,11** | [+0,99; +3,23] |
| primeira (piso) | 73,27% | **75,07%** | **+1,80** | [+0,36; +3,24] |

**É o resultado mais limpo do projeto até aqui.** Nenhuma outra medição melhorou
as quatro casas com o intervalo inteiro acima de zero em todas.

### ⚠ A previsão errou, e para cima

> **Previsão registrada: entre +1,2 e +2,2 pp.**

Deu **+2,56 pp** — **fora da faixa**, acima dela. Errei a terceira vez em quatro
previsões desta semana, e desta vez subestimando.

---

## A leitura, e ela é mais contida do que o número sugere

A tabela pré-registrada dizia:

> **acima de +2,2** → **sinergia** — o par vale mais que as partes

**Não vou reivindicar sinergia, por duas razões.**

### 1. A diferença para a soma não é estatisticamente distinguível

| | valor | erro padrão |
|---|---:|---:|
| soma dos efeitos isolados (1,03 + 0,88) | **1,91 pp** | 0,47 |
| efeito **conjunto** medido | **2,56 pp** | 0,31 |
| **diferença** | **+0,65 pp** | IC 95% **[−0,48; +1,78]** |

**O intervalo cruza zero.** O conjunto é compatível com a soma. Tratar +0,65 pp
como sinergia seria exatamente o erro que a régua quebrada nº 3 catalogou —
tomar um ponto estimado por um efeito.

### 2. E a própria soma não é uma referência válida

O T6 foi medido sobre o deck **v7**; o T10, sobre o **v9**. **Somar os dois é
somar medições feitas em estados diferentes do deck** — a mesma família da régua
quebrada nº 4, comparar sessões entre si.

> **A conclusão honesta:** a mudança de política vale **+2,56 pp** no deck atual,
> e isso está medido com o instrumento certo. **Se ela vale mais que a soma das
> partes, não dá para dizer** — e a soma das partes nem era um número
> comparável para começar.

---

## O que isto muda, e é bastante

**A política embarcada hoje é +2,56 pp melhor que a da última submissão** — e
isso é **só a política**. A diferença total contra o que está na ladder inclui
ainda o deck, que foi de `v6` para `v9` com três trocas aprovadas no gate
(+2,24, +1,04, +1,09) e uma adotada contra ele (+0,19).

| | medido |
|---|---:|
| política (T6 + T10), no deck atual | **+2,56 pp** |
| deck (v6 → v9) | não medido de ponta a ponta |

**O agente que está na ladder desde 15/08 é materialmente pior que o que temos**,
e agora isso é um número medido de uma vez só, não uma soma de parcelas.

### E resolve uma dúvida sobre o placar do projeto

O relatório diz "cinco aprovações". Alguém poderia perguntar se elas se
canceleram entre si. **Para as duas de política, não se cancelam** — o conjunto
entrega pelo menos o que as partes prometiam. É a primeira evidência
composicional que o projeto tem.
