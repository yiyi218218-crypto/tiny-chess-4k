# tiny-chess-4k

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/yiyi218218-crypto/tiny-chess-4k/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/yiyi218218-crypto/tiny-chess-4k/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A chess engine that fits in 4,096 bytes of Python. It plays the house gauntlet
through the env at `MAKEFUN_ENV_URL`, one game after another, and exits when the
trial is over.

## How it plays

A 120-square board with an off-board sentinel, white pieces 2-7 and black eight
above them, so a piece's kind is its value mod 8 and a colour test is one
comparison.

Evaluation is material plus piece-square tables, middlegame and endgame, blended
by a phase count of the non-pawn material still on the board: knights and bishops
one, rooks two, queens four, twenty-four at the start. A pawn on its seventh rank
is worth a hundred and seventy-eight more in the endgame than in the middle, which
is what turns a blocked passer into a reason to push it.

Search is iterative deepening alpha-beta with a transposition table, null-move
pruning at depth three and up, late move reductions that grow with the move index,
a quiescence search that searches every evasion when the side to move is in check,
killers, history, and MVV-LVA ordering. Moves are only re-tested for legality when
the king moves, when the piece is pinned, or when the move is en passant; a single
ray scan per node finds the pins.

Two details keep a trial reproducible. The search is bounded by a node count and
never by a clock, so the same position always spends the same effort; and the game
so far is replayed into a list of position hashes, so a move that would repeat a
position for the third time is scored as a draw rather than as a win it cannot
reach.

## Run it

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8080 python main.py
```

`main.py` is the lzma-packed entrypoint; `makefun compress` built it from a
readable source, which is not committed.

---

<sub>Entered on [make.fun](https://make.fun/?ref=y9aqxzyh&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
