# Deck–Policy Coupling in a Pokémon TCG Agent

Supporting material for the **Pokémon TCG AI Battle Challenge — Strategy
track**. Everything a judge needs to understand and verify the submission, and
nothing else.

```
The finding, in one line:

  a win rate is not a property of the agent — it is a property of the
  deck–policy PAIR, and the same policy is worth +7.5 points on the list
  it was built for and +0.7 on another

The honest result:

  ladder rating 304.4, rank 6,123 of 6,807 (median 618)
  the same 60 cards in other people's hands average 1,004
```

That second block is not a footnote. The agent is weak on the ladder, the
report says so in its own Limitations section, and the contribution offered
here is the measurement procedure that explains *why* a number like 304.4
cannot be attributed to the agent alone.

---

## Start here

| you want to | open |
|---|---|
| **read the submission** | [`report/REPORT.md`](report/REPORT.md) — 1,997 words |
| see the figures | [`report/figures/`](report/figures) — PNG and SVG |
| read the agent | [`agent/main.py`](agent/main.py) — single file, no imports beyond the engine |
| see the deck | [`agent/deck.csv`](agent/deck.csv) — 60 card IDs |
| check a number | [`measurement/`](measurement) — the script behind each claim |
| check the discipline | [`experiments/`](experiments) — hypotheses registered **before** each run |

---

## The finding

The project began as an attempt to build a strong agent and became an attempt
to measure one. Four independent measurements produced the same conclusion.

| measurement | what changed | result |
|---|---|---|
| **1** | the *opponent's* deck, its policy fixed | we won **53.9% → 16.7%** |
| **2** | *our* deck, our policy fixed | **51.7% → 35.8%** |
| **3** | our policy driving the field's dominant list | worth **+0.7 pp** |
| **4** | our policy driving a list that plays our attacker | worth **+7.5 pp** |

And the control that decided the reading: with **no policy on either side**,
our list still wins **89.2%** of that matchup. Most of the gap exists before
any agent plays a card.

The practical consequence, and the reason this matters beyond one competition:
**evaluating a deck requires declaring the policy that drives it**, and deck
choice comes *after* policy choice. A deck score measured under one policy does
not transfer to another.

---

## The agent

A three-layer fallback cascade with a guaranteed exit at every layer, because
the engine scores a timeout as a loss.

1. **One-turn search.** For every legal action the engine's forward model is
   called through to end of turn; hidden cards are filled once per decision
   (determinization), with the opponent's list sampled by its measured share of
   the field. Results are ranked by the evaluation function.
2. **Heuristic ordering** by action type, when the time budget runs out.
3. **First legal action**, on any exception.

The evaluation function is hand-written terms (prizes, knockouts, energy,
bench, accumulated damage) plus a **linear model** trained by imitation on
**335,101 decisions from 723 ladder games**. Features are standardized
(`z = (x − μ) / σ`) with mean and standard deviation embedded alongside the 50
weights.

It is linear by constraint, not by preference: the submission must be a single
file, and a tree model that beat it at imitation (+1.97 pp) does not fit.

> **Search depth is shallow because deeper measured worse**: two-turn search
> cost −4.9 pp and beam search −4.22. With hidden information and one
> determinization, state-estimate error grows faster than lookahead gain.

See [`report/figures/Figure-1-decision-flow.png`](report/figures/Figure-1-decision-flow.png).

---

## The deck

Built on **4× Teal Mask Ogerpon ex** — a basic attacker whose damage scales
without a ceiling with attached energy, untargetable on the bench (Tera), whose
ability *Teal Dance* attaches a Grass Energy and draws.

Concept and policy are the same object: the energy and damage terms of the
evaluation function *are* this card's game plan. That is why the policy
transfers to a list that plays the card and not to one that does not.

Utilisation was measured in play rather than assumed — and the corrections it
suggested were tested and **rejected**, which is reported as such:

| card | what the measurement found | verdict |
|---|---|---|
| Teal Dance | fires on **90.6%** of turns | — |
| Jumbo Ice Cream | **58%** (±10.3, n=89) of uses on Pokémon knocked out the same turn | policy fix **−0.89 pp**, rejected |
| Briar | played with **3.7 prizes** still to take | policy fix **−1.96 pp**, rejected |
| Judge | 15 of 18 strong lists run 4 copies | adopting it **−2.36 pp**, rejected |

---

## How the numbers were produced

Every claim in the report has a script here that produces it.

| claim in the report | script |
|---|---|
| win rate against the four reference opponents | [`measurement/painel.py`](measurement/painel.py) |
| deck A vs deck B with paired replicates | [`measurement/comparar_decks.py`](measurement/comparar_decks.py) |
| field composition and archetype shares | [`measurement/meta_atual.py`](measurement/meta_atual.py) |
| card utilisation (90.6%, 58%, 3.7 prizes) | [`measurement/medir_uso_cartas.py`](measurement/medir_uso_cartas.py) |
| consensus of strong lists (15 of 18, 14 of 14) | [`measurement/consenso_das_listas.py`](measurement/consenso_das_listas.py) |
| confidence intervals and significance | [`measurement/estatistica.py`](measurement/estatistica.py) |
| the four figures | [`measurement/figuras_writeup.py`](measurement/figuras_writeup.py) |
| the linear model, training and export | [`measurement/treinar_prior.py`](measurement/treinar_prior.py), [`exportar_prior.py`](measurement/exportar_prior.py) |

### The rules the project measured under

- **Pre-registration.** Hypothesis, values to test, a numeric prediction and a
  falsification table, written *before* the run. The result is appended without
  editing anything above it. All of them are in [`experiments/`](experiments).
- **A conjunctive acceptance criterion.** A change is adopted only if it raises
  the aggregate win rate against four reference opponents with a 95% interval
  above zero **and** regresses against none of them individually.
- **Replicates, always.** The engine accepts no random seed: four runs with
  identical decks and a deterministic agent produced 118 to 191 decisions in
  different sequences. There is no paired game.
- **A declared resolution.** Dispersion between runs is 1.39× the binomial
  prediction, so intervals computed under independence are 39% too narrow. The
  minimum detectable difference is **0.9 pp**, and effects below the bench's
  own reproducibility are not declared as results.

Of more than twenty hypotheses put to that criterion, **six passed**. A seventh
was adopted against it, by declared decision, and is labelled as such
everywhere it appears.

---

## Reproducing

```bash
python -m pip install -r requirements.txt

# the figures in the report, both languages
python measurement/figuras_writeup.py --idioma en --deck agent/deck.csv

# deck composition
python measurement/analisar_deck.py --deck agent/deck.csv

# word count of the report, four conventions
python measurement/contar_palavras.py report/REPORT.md

# the tests that lock the published artefacts
python -m pytest tests/ -q
```

---

## What is **not** in this repository, and why

- **The competition engine** (`cg`) is the organizers' and is not
  redistributable. Scripts that drive matches — `painel.py`,
  `arena_paralela.py`, `comparar_decks.py` — import it and will not run without
  it. They are here to be **read**: the measurement logic, the replicate
  handling and the interval arithmetic are all visible.
- **Ladder episode data** used to train the imitation model, for the same
  reason.
- **The working repository**: 80+ analysis scripts, 19 test modules and 65
  archived documents. Kept out on purpose — this repository is scoped to what a
  judge needs to evaluate the submission.
- **`experiments/` is in Portuguese.** These are the original pre-registrations
  and were deliberately not rewritten: editing them after the fact would
  destroy the only property that makes them evidence. Each file opens with the
  hypothesis, the numeric prediction and the falsification table, and closes
  with the measured result.

---

## License

[MIT](LICENSE).
