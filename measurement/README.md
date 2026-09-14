# Measurement

Every quantitative claim in the report was produced by one of the scripts in
this directory. The table below names which.

The scripts carry Portuguese names and Portuguese comments, because they are
the working instruments rather than a presentation layer written afterwards,
and renaming them would break the correspondence with the pre-registrations
that cite them. What each one measures, and which claim it supports, is set out
here in full.

---

## Which script backs which claim

| claim in the report | produced by |
|---|---|
| aggregate win rate against the four reference opponents, and the conjunctive criterion that gates every adopted change | `painel.py` |
| deck A against deck B under paired replicates, the instrument that replaced the panel for list comparisons | `comparar_decks.py` |
| the parallel arena underneath both of the above, which runs the matches | `arena_paralela.py` |
| confidence intervals, dispersion against the binomial prediction, and the significance arithmetic | `estatistica.py` |
| composition of the competitive field and the share held by each archetype | `meta_atual.py` |
| card usage in play: the 90.6% ability rate, the 58% wasted healing, the 3.7 prizes left on the board | `medir_uso_cartas.py` |
| the consensus of strong lists, including *15 of 18* and *14 of 14* | `consenso_das_listas.py` |
| composition of the list by card type | `analisar_deck.py` |
| resolution of the deck actually under measurement | `deck_em_uso.py` |
| the linear model: training on the imitation corpus, and export as embedded constants | `treinar_prior.py`, `exportar_prior.py` |
| the five figures in the report, in both languages | `figuras_writeup.py` |
| the word count of the report under four counting conventions | `contar_palavras.py` |
| the pre-submission checklist over the packaged agent | `conferir_submissao.py` |

---

## Two properties worth noticing in the source

**Figures are generated, never transcribed.** `figuras_writeup.py` reads the
same sources as the tables in the report. The project transcribed a number by
hand exactly once, published it wrong, and adopted the rule afterwards. The
figure of the decklist is generated from the deck file and the official card
catalogue, so it cannot drift from what the agent actually plays.

**New instruments ship with a control against themselves.** After a screening
tool was found to be measuring its own noise, every measurement script built
afterwards compares the baseline against itself as a control. One defect was
caught by that rule before it affected any decision, which is the only case in
the project where an error was found before it cost something.

---

## What runs from this repository, and what does not

The competition engine is the organisers' property and is not redistributed
here, and neither are the ladder episodes behind the imitation corpus.
`painel.py`, `arena_paralela.py` and `comparar_decks.py` drive matches through
that engine and therefore cannot execute standalone; they are included so that
the replicate handling, the interval arithmetic and the controls can be read
and checked.

`figuras_writeup.py`, `analisar_deck.py`, `deck_em_uso.py`, `estatistica.py`
and `contar_palavras.py` depend on nothing beyond the repository and the
standard library, and reproduce their outputs directly.
