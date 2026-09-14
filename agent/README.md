# The agent

`main.py` is the agent as submitted, and `deck.csv` the sixty cards it plays.

## Why a single file

The competition packages a submission as one module, and nothing outside it is
guaranteed to exist at runtime. Discovering that cost three submissions: code
that resolved paths relative to its own location worked locally and failed in
the container, where that variable is not defined. Everything the agent needs
is therefore embedded, including the fifty model weights, the per-feature means
and standard deviations, and the generated damage tables.

That constraint is also why the learned component is linear. A tree model
outperformed it at imitation by 1.97 percentage points and does not fit;
distilling a hundred trees into linear form cost 0.40 percentage point of win
rate, so the constraint was accepted rather than circumvented.

## How a decision is made

The entry point is called once per decision and has two distinct outputs. On
the first call of a match the engine asks for the deck rather than for a play,
and the agent returns the sixty card identifiers; on every call afterwards it
returns a selection of legal action indices.

For a play, three layers are tried in order and each has a guaranteed exit.

The principal layer searches one turn deep. For every legal action the engine's
forward model is applied and the line carried through to the end of the turn.
Hidden cards are resolved once per decision by determinization: our own unseen
cards are shuffled, and the opponent's list is sampled from the archetypes of
the competitive field weighted by their measured share. Each resulting state is
scored by the evaluation function, which combines hand-written terms over
prizes, knockouts, energy, bench and accumulated damage with the standardised
linear model.

When the time budget runs out, the decision passes to a heuristic layer that
orders actions by type against a fixed priority scale. If either layer raises,
a third takes the first legal action. That final layer exists because the
engine scores a timeout as a loss, so an unhandled exception would cost the
match rather than the turn.

All three converge on the same selection routine, which sorts by score and
applies the engine's minimum and maximum selection counts. That routine is
where the output invariants are enforced: indices in range, no duplicates, and
a count the engine will accept.

## Reading the source

The comments are in Portuguese and are unusually dense, because the file
doubles as the record of what the engine actually does as opposed to what its
documentation implies. Several of them mark behaviour that cost a submission or
a week of measurement to discover: that the Pokémon in play exposes current hit
points but not the fields needed to compute damage, that weakness doubles
damage while resistance subtracts a fixed amount with a floor at zero, and that
the opening hand is never dealt without a basic Pokémon regardless of how few
the list runs.

The deck file is a plain list of card identifiers, one per line, resolved
against the official catalogue at build time. No card is referenced by name
anywhere in the agent, which is what allows the list to be replaced without
touching the code, and which in turn is what made the deck–policy measurements
in the report possible at all.
