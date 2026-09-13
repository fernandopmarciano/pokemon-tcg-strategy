# Deck–Policy Coupling in a Pokémon TCG Agent

## 1. Objective

A win rate is customarily reported as a measure of the agent that produced it.
This work shows that in the Pokémon Trading Card Game the attribution does not
hold, and gives a procedure that separates the two factors responsible.

The procedure fixes one factor and varies the other. Applied four times, it
shows that changing only the card list moves the same agent from 51.7% to 35.8%
of wins, and that the same decision policy is worth 7.5 percentage points on
the list it was designed for and 0.7 on a list that does not play its attacker.

It follows that a win rate is interpretable only with the list and the policy
declared together, and that a deck must be chosen after the policy that will
drive it, never before. This is the contribution offered here, and it
generalises beyond one archetype and one competition.

## 2. Architecture and rationale

Figure 1 gives the decision path, its inputs and its two exit points.

> **Figure 1.** Inputs, decision ladder and the two exit points.

The main layer searches to a depth of one turn. For each legal action the
engine's forward model, the function applying an action to a state and
returning the resulting one, is called through to the end of the turn. Unknown
cards are filled in once per decision, a procedure called determinization, with
the opponent's list sampled by its measured share of the field. When the time
budget runs out a heuristic layer orders actions by type, and on any exception
a third layer takes the first legal action. Every layer has a guaranteed exit
because the engine scores a timeout as a loss.

Shallow search is a measured decision rather than a concession. Two-turn search
cost 4.9 percentage points and beam search 4.22: with hidden information and a
single determinization, the error in estimating the future state grows faster
than the gain from looking further ahead. Depth was therefore spent on
completing the turn instead.

The evaluation function combines hand-written terms, covering prizes,
knockouts, energy, bench and accumulated damage, with a linear model trained by
imitation on 335,101 decisions from 723 ladder games by players averaging about
1,100 rating. Features are standardised before the weighted sum, with mean and
standard deviation embedded alongside the fifty weights.

The model is linear by constraint: the submission must be a single file, and a
tree model that beat it at imitation by 1.97 percentage points does not fit.
Distilling a hundred trees into linear form cost 0.40, so the constraint was
accepted rather than worked around.

Damage tables are generated from the official catalogue, covering 1,004 cards
and 1,555 attacks, with no hand-written card identifiers. Changing the list
therefore requires no code change, and that property is what makes the
measurements in section 4.1 possible at all.

## 3. Experimental protocol

The protocol is itself a result. Eleven early measurements produced conclusions
that later collapsed, five of them caught by numerical inconsistency rather
than by code review, and each collapse added a rule that the bench has enforced
since. The most instructive filtered an archetype by its list label over 14% of
the real population: a conclusion that survived Bonferroni correction and two
controls reversed sign once the denominator was fixed. No statistical control
protects against a wrong denominator, so every new instrument now ships with a
control that compares the baseline against itself.

The rules that came out of it:

Nothing is adopted without a criterion declared before measurement. That
criterion is conjunctive: a change must raise the aggregate win rate against
four reference opponents with a 95% interval above zero, and must not lower it
against any of them individually.

Every hypothesis is registered before the run, with the values to test, a
numeric prediction and a falsification table. The result is appended without
editing anything above it.

Every comparison uses replicates. The engine accepts no random seed, and four
runs with identical decks and a deterministic agent produced between 118 and
191 decisions in different sequences, so no two games are paired. Dispersion
between runs of the same agent against the same opponents is 1.39 times the
binomial prediction, which means intervals computed under independence are 39%
too narrow.

The bench declares its own resolution. Two batches of ten replicates of the
same binary, run at different times, gave 51.93% ± 0.67 and 52.09% ± 0.80
(Figure 2). The distance between those means is the reproducibility of the
procedure, and effects smaller than 0.9 percentage point are not reported as
results.

> **Figure 2.** Thirty replicates of 4,400 games: two batches of the same agent
> measure the noise; the third carries the adopted correction.

## 4. Results

### 4.1 Coupling between list and policy

The first measurement took the best-placed public agent available, against
which the agent described here won 53.9% of games. Its heuristics reference six
cards by identifier, and the configuration measured had it driving a list other
than the one it was written for. Given its own list, and with its policy
untouched, the rate fell to 16.7%. Thirty-seven percentage points moved with
the cards alone.

The clue that opened the investigation was an inversion: granting that opponent
ten times more search time raised our win rate. Longer search only hurts when
the function being optimised is misaligned with the real position, which is
exactly what happens when heuristics reference cards that are not in the deck.
That inversion is now a permanent detector on the bench, run at two search
budgets so it fires again if any future opponent is misconfigured.

The second measurement applied the same procedure to the agent described here.
With its own list the aggregate rate against the four reference opponents is
51.7% [50.5; 52.9]; with the organisers' sample list, 35.8% [34.0; 37.6], a
drop of 15.9 percentage points that holds against all four opponents
individually.

The third and fourth put the policy on the opponent's side and measure what it
recovers there. Driving the field's dominant list it takes that side from 0.3%
to 1.0% of wins, worth 0.7 percentage point. Driving a list that runs four
copies of our own attacker it takes that side from 5.4% to 12.9%, worth 7.5
percentage points [+6.1; +8.9], ten times as much.

The control on the fourth measurement is what settles the section. With no
policy on either side, the list alone still wins 89.2% [88.0; 90.2] of that
matchup. Of the 94.6% won with a policy on one side, 89.2 points belong to the
list and 5.5 to the policy. The mirror, list against itself, returns 48.4%
[46.6; 50.2], confirming the arena is unbiased. Most of the outcome is decided
before either agent plays a card, and that is the finding.

> **Figure 3.** Measured effect of each hypothesis in percentage points of win
> rate, with a 95% interval.

### 4.2 Auditing the learned model

The imitation model had been checked against random choice and against the
heuristic by action type, and beat both. The baseline that mattered was
missing: always taking the first action the engine returns.

| sample | model | random | first action |
|---|---:|---:|---:|
| 25,479 decisions, all archetypes | 34.7% | 22.5% | 34.7% |
| 8,799 decisions, independent sample | 34.8% | 22.8% | 35.2% |
| 3,304 decisions, own archetype only | 59.2% | 21.3% | 61.8% |

Across three independent samples the model matches that trivial rule. The cause
is in the input representation: of fifty variables only three describe the card,
so two distinct support cards produce identical vectors, and the heaviest
variable, weighted 9.4 times the second, is the position of the action in the
engine's own list.

Asking whether the model did anything at all, rather than how to improve it, is
what produced the three corrections in section 4.3, which are the largest
adopted gains in the project.

### 4.3 Corrections to the evaluation function

Comparing decisions one by one against players above 1,000 rating driving the
same list exposed three defects of a single kind: value assigned to states that
are not progress.

**Priority order.** In 143 of the 143 turns where those players ended their
turn, the agent did not. Two corrections were registered in advance, one above
and one below the model's threshold, the second as a control. The predicted
value returned +1.10 and the control +1.03. Under the registered hypothesis the
control should have returned zero, so the proposed explanation was discarded
and replaced by the one the data supports: what the two share is the relative
order of actions, not the distance between them on the scale.

**Bench energy.** The function weighted energy on the bench equally with energy
on the active Pokémon, although the attack consumes only the latter. Distinct
states scored identically and the tie fell through to the action index, which
started 23.7% of turns with the wrong Pokémon. Giving bench energy zero weight
returned +0.88 [+0.33; +1.43], positive in nine of ten paired replicates.

**Hit points.** The function summed the active Pokémon's hit points alone, so
retreating a damaged attacker and promoting a fresh one raised the score by 150
while healing nobody. Replacing it with a penalty on damage across the whole
field, invariant to rotation, returned +0.59 [+0.09; +1.09] over 20 replicates.

Together these are worth 2.56 percentage points [+1.90; +3.22] of policy gain,
measured before the last of them and therefore a lower bound.

### 4.4 The deck: concept and utilisation

The list is built on four Teal Mask Ogerpon ex: a basic attacker whose damage
scales without a ceiling with attached energy, untargetable on the bench
because it is Tera, and whose ability Teal Dance attaches a Grass Energy and
draws a card.

Concept and policy are the same object. The energy and damage terms of the
evaluation function are this card's game plan, which is precisely why the
policy is worth 7.5 points on a list that plays the card and 0.7 on one that
does not. The remaining cards serve that plan: twenty-four energy, four Tera
Orb and four Bug Catching Set to find the attacker, two Lively Stadium, and one
Hero's Cape (Figures 4 and 5).

Utilisation was measured in play rather than assumed, and every correction it
suggested was put to the same criterion. Teal Dance fires on 90.6% of turns.
Jumbo Ice Cream was spent on Pokémon knocked out the same turn in 58% of uses
(±10.3, n=89) and Briar, a closing card, was played with 3.7 prizes still to
take; policies correcting both were built, measured at −0.89 and −1.96, and not
adopted. Measuring a card's use is not the same as improving it, and the
criterion was applied to our own proposals as strictly as to any other.

Four divergences from the consensus of strong lists were tested with the
hypothesis registered first, two approved and two rejected. Adopting four
Judge, which 15 of 18 strong lists run, would cost 2.36 percentage points;
cutting Night Stretcher from three copies to one gained 1.09. Consensus is
right about half the time, and only measurement says which half.

> **Figure 4.** The sixty cards by function: one attacker; the rest is search,
> energy and recovery.

> **Figure 5.** The decklist, card by card: one attacker; the rest searches,
> accelerates energy and recovers.

### 4.5 Robustness to opening state and matchup

The acceptance criterion forbids regressing against any single opponent, which
structurally prevents adopting a change that wins on aggregate by sacrificing
one matchup. That rule was tested against its hardest case. Against the worst
matchup measured, Hero's Cape raises the attacker past the opposing attack's
damage ceiling, turning a one-hit knockout from certain into impossible on the
commonest attack line. The bench recorded a tie, +0.19, and the card was
adopted anyway by declared decision, the single documented exception, because
the mechanism was verifiable in the official damage tables even where the four
reference opponents could not see it.

The remaining dependency is on field composition, and it is declared rather
than defended: three weeks after the list was derived, the archetype it was
built to beat had fallen to 0.5% of the field. Any deck derived against a
measured field inherits the shelf life of that measurement, which is one more
reason deck choice belongs downstream of policy.

## 5. Scope and instrument limits

The four reference opponents belong to an archetype accounting for 1.5% [1.0;
2.1] of the measured field, and the only strong public opponent plays well only
with its own list. Every result above is therefore stated for that bench and
not for the field at large, and measuring against the live field was not
possible because neither that opponent nor this agent drives arbitrary lists.

The associated simulation ladder proved to be the least informative instrument
available, and discovering that is what justified building the bench used here.
Three submissions of an identical file scored 413.6, 385.0 and 308.3, a spread
of 105 rating points, which is larger than the difference between any two
versions of the agent. A ladder that cannot separate a file from itself cannot
arbitrate a 0.9-point effect, so the paired-replicate bench, with its declared
resolution and its conjunctive criterion, replaced it as the decision
instrument for the whole project.

## 6. Conclusion

More than twenty hypotheses were put to a criterion fixed before measurement.
Six passed and a seventh was adopted against it by declared decision. Effects
large enough to matter were resolved with intervals excluding zero, and effects
below the bench's own reproducibility were reported as undetermined rather than
as gains.

The method that produced every adopted improvement was to stop asking how to
improve the model and start asking whether it beat a trivial baseline. It did
not, and the answer to that question is what the three largest gains in this
project came from.
