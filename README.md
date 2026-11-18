# tiny-chess-4k

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/yiyi218218-crypto/tiny-chess-4k/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/yiyi218218-crypto/tiny-chess-4k/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A compact chess engine for the [tiny-chess-01](https://make.fun/bounty/tiny-chess-01) gauntlet. It polls `MAKEFUN_ENV_URL`, plays one legal move per turn and exits when the trial ends.

The board is a ten-wide mailbox with a sentinel ring; white men are codes two to seven, black men the same codes eight higher. Scores are material plus middlegame and endgame piece-square tables, mixed by a phase count, from a 768-character packed blob, with a bishop pair bonus and a tempo term on top. Search is iterative-deepening alpha-beta with a transposition table, null moves, late-move reductions, a capture-only quiescence and a node budget. Killers, history and MVV-LVA order the moves; the mover's king is tested after each move, stalemate scores a draw and a position already seen twice in the game scores zero. Deepening stops at a 5-second wall-clock mark and the best move found so far is played, keeping every move well inside the ten-second allowance.

```sh
MAKEFUN_ENV_URL=http://127.0.0.1:8080 python main.py
```

`main.py` is the packed entry; its readable source is not committed. Three practice trials scored 3.5 to 5.0 points from six games each — about 1,490 Elo on the anchor curve — with no game lost on time and a slowest move of 5.2 seconds against the ten-second allowance.
