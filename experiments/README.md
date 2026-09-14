# Pre-registrations

Sixteen experiments, each registered before it was run.

The format is fixed and was never departed from. Every document opens with the
question, the values to be tested, a numeric prediction of the outcome, and a
falsification table stating in advance which results would count as refuting
the hypothesis. The measured result is appended in a closing section, and
nothing above that section is edited afterwards. Where a conclusion was later
retracted, the retraction is added as a marked block rather than applied as a
silent correction.

That format is the reason these files are published unaltered and in their
original Portuguese. A pre-registration rewritten after its result is known is
no longer a pre-registration, and translating a dated document would require
touching text whose value depends on not having been touched. The table below
therefore carries the full evidentiary content in English: the question each
experiment asked, the prediction registered in advance, the measured effect
with its interval, and the verdict.

Effects are in percentage points of win rate, measured against a fixed panel of
four reference opponents. Intervals are 95%. The acceptance criterion was
conjunctive: a change had to raise the aggregate with an interval above zero
**and** not regress against any single opponent.

---

## The experiments

| | question asked in advance | measured | verdict |
|---|---|---|---|
| **T1** | Does replacing the stadium card change the aggregate? | **+1.04** | **adopted** |
| **T6** | The agent never ends its turn when strong players do. Is the cause the priority scale, and does compressing the distance between `ATTACK` and `END` fix it? | **+1.03** predicted value, **+1.10** control | **adopted** — and the registered explanation was falsified by its own control |
| **T7** | Should attaching energy outrank playing a card, or is the ordering already correct? | **+0.09** [−0.56; +0.74] | tie, not adopted — the outcome predicted in advance |
| **T8** | Sixteen of sixteen strong lists play a defensive tool we do not. Does adding it pay? | **+0.19** [−0.44; +0.82] | **tie, adopted anyway** by declared decision — the single documented exception, taken because the mechanism was verifiable in the damage tables even where the panel could not see it |
| **T9** | Does the list run too many copies of a recovery card that no strong list plays? | **+1.09**, replicated at **+0.61** | **adopted** |
| **T10** | The evaluation weights bench energy equally with active energy, but the attack consumes only the active. Does separating them fix the 23.7% of turns that start with the wrong Pokémon? | **+0.88** [+0.33; +1.43] | **adopted**, positive in nine of ten paired replicates |
| **T11** | Is what matters the *ordering* of the energy terms, or the *magnitude* of the gap? | **+0.19** [−0.37; +0.75] | tie — ordering is what pays; magnitude within the tested range does not |
| **T12** | Do the individually adopted gains still add up when combined? | **+2.56** [+1.90; +3.22] | confirmed, over the version that reached the ladder |
| **T13** | The evaluation sums only the active Pokémon's hit points, so retreating a damaged attacker raises the score by 150 while healing nobody. Does a rotation-invariant damage penalty fix it? | **+0.59** [+0.09; +1.09] | **adopted**, twenty replicates |
| **T14** | Audit of every evaluation input: which terms describe something the agent controls? | — | produced the rule that state evaluation pays only when it corrects something the agent controls |
| **T15** | The damage term was rejected at −7.37 before the priority scale was rebalanced. Does it pay now? | **−0.22** [−0.67; +0.24] | tie, not adopted — the same term went from heavily negative to inert without a line changing, because the scale around it changed |
| **T16** | Should the opponent's accumulated energy count against our evaluation? | **+0.10** [−0.24; +0.43] | tie, not adopted — prediction correct on both point and verdict |

## The three investigations

| | question | outcome |
|---|---|---|
| **h-banco** | Strong players leave the attacker on the bench far more often than we do. Is there an identifiable trigger? | **Retracted and remeasured in the same day.** The archetype had been filtered by the list's label over a sample that was 14% of the real population. Corrected, the base rate is 38.0% [35.7; 40.3], none of the four pre-registered triggers survives, and the strongest of them inverted sign when the sample grew from 22 turns to 416. What separates the behaviour is the deck shell, not player rating. |
| **h-casa** | Can a second strong opponent be built by having our own policy drive a field list? | The policy recovers **+7.5** [+6.1; +8.9] for the side it drives, ten times its value on a list that does not play our attacker. **The control overturned the optimistic reading**: with no policy on either side, our list already wins **89.2%** [88.0; 90.2]. The matchup is decided by list complexity, not by the pilot. |
| **R1 / R2** | The learned model was credited with +10.11. Does that survive the current instrument? | **It does not.** Three measurements place the effect between **−0.80 and +0.27**. The model was never changed; the priority scale it operates on was rebalanced between the two measurements. Two of the four replication runs terminated without an identifiable cause, which is recorded here rather than omitted, and the conclusion is stated only to the strength the completed runs support. |

---

## What the record shows

Twelve numbered experiments and three investigations, of which six changes
passed the criterion and were adopted, one was adopted against it by declared
decision, and the remainder failed. The failures are published at the same
length as the successes.

Two entries are worth reading even by someone uninterested in the game. **T6**
is a case where the hypothesis passed the acceptance criterion while the
control that was registered alongside it destroyed the proposed explanation, so
the change was kept and the reasoning behind it discarded. **h-banco** is a
case where a conclusion that had survived Bonferroni correction and two
independent controls turned out to rest on a wrong denominator, and reversed
sign once the denominator was fixed. No amount of statistical control protects
against a mis-specified population, which is why every instrument built after
that date ships with a control comparing the baseline against itself.
