# tiny-chess-4k

A compact chess engine for the tiny-chess-01 gauntlet. It talks to the match
server through `MAKEFUN_ENV_URL`, asks for a game, plays one legal move at a
time, and stops when the server reports that the trial is done.

## What is inside

The position lives in a ten-wide mailbox. Rows two through nine hold the board
and a sentinel ring surrounds it, so a knight or king step can never wander off
the edge and a sliding piece stops by itself. White men occupy codes two to
seven, black men the same codes eight higher; taking a code modulo eight gives
the piece kind, and one comparison gives its colour.

Scores come from material plus two sets of piece-square tables. A phase counter
weights a knight or bishop as one, a rook as two and a queen as four, and the
tables are mixed accordingly across the twenty-four points of material in the
starting position. The tables themselves are stored as a single string of
characters, twelve blocks of sixty-four, at eight-centipawn resolution.

The search deepens one ply at a time and stops after a fixed number of nodes,
never on the wall clock, so a position always receives a repeatable amount of
work. A hash table holds earlier results with bound types and depths; null
moves, late move reductions and a capture-only quiescence prune the tree. At the
root the previous best move is tried first, then captures, with a narrow window
for every later move. Killers, history scores and most-valuable-victim ordering
decide the rest.

Legality is handled by making the move and looking at the mover's king, then
taking the move back if that king is still attacked. Running out of moves is
mate when in check and a draw otherwise — a stalemate must not be mistaken for
a win. A hash list of the game so far turns a third repetition into a draw.
Should the chosen move ever be rejected, the engine falls back to the first
move the server offered rather than crashing the whole trial.

## Build and run

`main.py` is the packed entrypoint, produced from a source file that is kept
out of the repository.

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8080 python main.py
```

## Checking the work

The source was compared with a known-good build on fixed positions at several
node budgets, checking both the move and the node count. Practice trials run
the packed entry against the house opponents and report score and think time.

A first practice trial scored two wins and four losses, worth roughly 1,099
Elo, with 121 plies spared in the wins and a slowest move of about 5.6 seconds
against a ten-second allowance. The packed entry is exactly 4,096 bytes; the
source stays untracked and travels with the session record.
