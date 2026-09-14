# Deck–Policy Coupling in a Pokémon TCG Agent

Supporting material for the Pokémon TCG AI Battle Challenge, Strategy track.

A win rate is customarily reported as a measure of the agent that produced it.
The work collected here shows that in the Pokémon Trading Card Game the
attribution does not hold, and offers a procedure that separates the two
factors actually responsible: the sixty-card list, and the decision policy that
drives it. Four independent measurements support the claim, and a control
measurement determines how it should be read.

The submission itself is [`report/REPORT.md`](report/REPORT.md). Everything
else in this repository exists to let a reader verify it rather than accept it.

---

## How the finding was reached

The project began as an attempt to build a strong agent and became an attempt
to measure one, and the turn happened by accident.

While benchmarking against the strongest public agent that could be obtained,
an anomaly appeared that should not have been possible: granting that opponent
ten times more thinking time consistently *improved* our own win rate. Search
that looks further ahead only degrades play when the function being optimised
is misaligned with the position on the table, which pointed at the opponent's
evaluation rather than at ours. Inspection confirmed it. Its heuristics
reference six cards by numeric identifier, and the benchmark had been running
it on a deck it was never written for. Restoring its own list, and changing
nothing about its policy, moved our result from 53.9% to 16.7%.

Thirty-seven percentage points had been attributed to an agent and belonged to
the cards. That raised the obvious question about our own numbers, and the rest
of the project is the attempt to answer it honestly: fix one factor, vary the
other, and see how much of a win rate survives.

It does not survive well. Our own agent, policy untouched, falls from 51.7% to
35.8% when handed a different list. The same policy is worth 7.5 percentage
points over a null baseline on a list that plays the card its evaluation
function was designed around, and 0.7 on a list that does not. And the control
that settles the matter: with no policy on either side at all, our list still
wins 89.2% of the matchup where the policy appeared most valuable. Most of the
outcome is decided before either agent plays a card.

The practical consequence reaches past this competition. A deck evaluated under
one policy tells you nothing about that deck under another, so deck selection
belongs downstream of policy selection, never before it.

---

## What is here, and why each part earns its place

**[`report/`](report)** holds the submission and the five figures that carry
its quantitative claims. The figures are generated from the same sources as the
tables, never transcribed by hand, because transcription introduced a wrong
number once and the project stopped trusting it.

**[`agent/`](agent)** holds the agent as submitted and the sixty cards it
plays. The agent is a single file by requirement of the competition packaging,
and that constraint shaped the model: a tree model that outperformed the linear
one at imitation does not fit inside it. The deck is included because, given
the finding above, publishing a policy without the list it was measured on
would reproduce exactly the error this work describes.

**[`measurement/`](measurement)** holds the scripts that produced the numbers.
Every quantitative claim in the report traces to one of them, and the index in
that directory names which script backs which claim. They are here to be read
as much as run: the replicate handling, the interval arithmetic and the
controls are all visible in the source.

**[`experiments/`](experiments)** holds sixteen pre-registrations. Each states
a hypothesis, the values to be tested, a numeric prediction and the table of
outcomes that would falsify it, all written before the run; the measured result
was appended afterwards without editing anything above it. Six of these changes
passed and were adopted, one was adopted against the criterion by declared
decision, and the rest failed. They are published in full, failures included,
because a pre-registration that is only shown when it succeeds is not evidence
of anything.

**[`tests/`](tests)** holds the invariants that protect the published
artefacts: that a figure never renders blank, that the deck under measurement
is the deck that ships, that a silently broken model degrades loudly instead of
quietly. Each exists because the corresponding failure happened.

---

## The agent

The agent decides in three layers, each with a guaranteed exit, because the
engine scores a timeout as a loss.

The principal layer searches one turn deep. For every legal action, the
engine's forward model is called through to the end of the turn; hidden cards
are resolved once per decision by determinization, with the opponent's list
sampled according to its measured share of the competitive field. Candidate
lines are ranked by an evaluation function. When the time budget is exhausted a
heuristic layer orders actions by type instead, and any unhandled exception
falls through to a layer that takes the first legal action.

Shallow search is a measured decision rather than a limitation accepted for
convenience. Searching two turns cost 4.9 percentage points and beam search
4.22. Under hidden information with a single determinization, error in the
estimate of the future state accumulates faster than lookahead repays, so depth
was spent on completing the current turn rather than on reaching the next.

The evaluation function combines hand-written terms over prizes, knockouts,
energy, bench and accumulated damage with a linear model trained by imitation
on 335,101 decisions drawn from 723 ladder games. Features are standardised
before the weighted sum, with the per-feature mean and standard deviation
embedded alongside the fifty weights.

The most consequential thing learned about that model is that it did not beat a
one-line rule. Audited against a baseline that simply takes the first action
the engine offers, it tied across three independent samples, because the
heaviest of its fifty features turned out to be the position of the action in
the engine's own list. Asking whether the model did anything at all, rather
than how to improve it, is what produced the three largest adopted gains in the
project.

---

## The deck

The list is built on four copies of Teal Mask Ogerpon ex: a basic attacker
whose damage scales without a ceiling as energy accumulates, untargetable while
on the bench because it is Tera, and whose ability attaches a Grass Energy and
draws a card each turn.

Concept and policy are the same object here, which is the local form of the
general finding. The energy and damage terms of the evaluation function are a
description of this card's game plan, and that is precisely why the policy
transfers to a list that plays the card and not to one that does not.

Card usage was measured in play rather than assumed, and the corrections that
measurement suggested were held to the same standard as any other proposal.
Three of them failed and were not adopted. The healing card was being spent on
Pokémon that were knocked out the same turn in 58% of its uses, and the closing
card was being played with 3.7 prizes still on the board; policies correcting
both were built, measured, and rejected at −0.89 and −1.96 percentage points.
Diagnosing a misuse and repairing it profitably are different problems, and the
criterion was applied to our own proposals without exception.

---

## The discipline the numbers were produced under

The protocol is itself one of the results, because it was assembled from
failures. Eleven early measurements yielded conclusions that later collapsed,
five of them caught by numerical inconsistency rather than by code review, and
each collapse contributed a rule that has been enforced since. The most
instructive filtered an archetype by the label on its list rather than by the
card of interest, over a sample that turned out to be 14% of the real
population; a conclusion that had survived Bonferroni correction and two
independent controls reversed sign once the denominator was fixed. No
statistical control protects against a wrong denominator, and every instrument
built afterwards ships with a control comparing the baseline against itself.

Four rules came out of that history. Nothing is adopted without a criterion
declared before measurement, and the criterion is conjunctive: a change must
raise the aggregate win rate against four reference opponents with a 95%
interval above zero and must not reduce it against any of them individually.
Every hypothesis is registered in advance with a numeric prediction and a
falsification table. Every comparison uses replicates, because the engine
accepts no random seed and no two games are paired. And the bench declares its
own resolution: dispersion between runs of an identical binary is 1.39 times
the binomial prediction, so effects below 0.9 percentage point are reported as
undetermined rather than as gains.

Of more than twenty hypotheses put to that criterion, six passed.

---

## Scope of what is published

The competition engine is the organisers' and is not redistributed here, nor
are the ladder episodes used to train the imitation model. Scripts that drive
matches therefore cannot execute from this repository alone, and are included
for inspection of their method rather than for immediate reproduction. The
figures, the deck analysis, the word count and the test suite run unaided.

The working repository from which this material was drawn contains eighty
analysis scripts and sixty-five archived documents. It is deliberately not
mirrored here. This repository is scoped to what is necessary to evaluate the
submission, and a reader should be able to reach any claim in the report within
two clicks of this page.

One editorial decision deserves stating plainly. The pre-registrations and the
comments inside the source are in Portuguese, the language they were written
in. They were not retranslated, because a pre-registration edited after its
result is known stops being evidence, and rewriting dated documents would
destroy the only property that makes them worth publishing. Each directory
therefore carries an English index that reproduces the hypothesis, the
registered prediction and the measured outcome, so that the evidentiary content
is fully available in English while the originals remain untouched.

---

## License

Released under the [MIT License](LICENSE).
