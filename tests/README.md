# Tests

Each of these exists because the corresponding failure happened once.

They are not a coverage exercise. They lock the invariants that protect what
gets published, on the principle that a defect which is invisible in the output
will be repeated.

| test | the invariant, and the failure that motivated it |
|---|---|
| `test_figuras_writeup.py` | A figure must parse as valid SVG, must not depend on CSS variables, and every effect it plots must carry an interval. An earlier chart module inherited its colours from the surrounding page, which rendered the figure invisible outside it. The suite also requires that every label exist in both languages and that the verdict survive translation, so a figure cannot silently lose the mark distinguishing an adopted change from a rejected one. It further pins the default deck to the list in use, after a figure was published showing the composition of a superseded one. |
| `test_deck_em_uso.py` | The deck under measurement must be the deck that ships. A search routine once filled its simulated deck with a list that was not in play, which inverted a deck decision from rejected to strongly positive once corrected. |
| `test_prior_guarda.py` | If the model's feature vector and its weights disagree in length, the agent must degrade loudly. Without the guard the mismatch was swallowed by an exception handler, silently disabling the learned component while the agent carried on playing worse and no test noticed. |
| `test_agent.py` | The agent must return a legal selection under every path, including the first call of a match, where the engine asks for the deck rather than for a play. That path does not exist in the local harness and was only exercised by a failed submission. |
| `test_opcoes_reais.py` | Option handling is checked against the shape the engine actually produces rather than the shape its documentation suggests. |
| `test_comparar_decks.py` | The paired-replicate comparison must handle interrupted runs without silently combining partial results, after two replication attempts terminated early and their partials disagreed with each other. |
