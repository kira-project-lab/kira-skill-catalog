# Robust leaderboard scoring

Use this when Maxim needs a float `LeaderboardScore` for an ML competition / hackathon-practice and there is no organizer baseline.

## Preferred no-baseline formula

For valid submits, compute score from private leaderboard metric using robust percentile bounds. For invalid or missing submit:

```text
LeaderboardScore = 0
```

For error metrics where **lower is better**:

```text
BestBound = P10(PrivateScore)
WorstBound = P90(PrivateScore)
q = (WorstBound - TeamScore) / (WorstBound - BestBound)
q_clipped = min(1, max(0, q))
LeaderboardScore = 2 + 8 * q_clipped
```

For metrics where **higher is better**:

```text
BestBound = P90(PrivateScore)
WorstBound = P10(PrivateScore)
q = (TeamScore - WorstBound) / (BestBound - WorstBound)
q_clipped = min(1, max(0, q))
LeaderboardScore = 2 + 8 * q_clipped
```

## Interpretation

- No valid submit: `0`.
- Valid submit at or worse than `WorstBound`: `2`.
- Valid submit between robust bounds: continuous score from `2` to `10`.
- Valid submit at or better than `BestBound`: `10`.

This separates “no technical result” from “valid but weak technical result” without over-rewarding the bottom of the leaderboard.

## Why P10/P90

For 100–150 participants in teams of 2–4, expect roughly 25–75 teams. In that range, P10/P90 is usually more stable than P5/P95: it ignores extreme weak submits and suspiciously strong outliers while preserving enough spread for float scoring.

If there are very few valid teams, either use less aggressive bounds only after inspecting the distribution, or explicitly state that organizers may adjust percentile bounds before publication.

## Example for lower-is-better metric

Private scores:

```text
118.0, 121.5, 124.0, 127.0, 130.0, 134.0, 138.0,
142.0, 147.0, 153.0, 160.0, 170.0, 190.0, 260.0
```

Bounds:

```text
BestBound = 122.25
WorstBound = 184.00
```

| Team | Private score | q_clipped | LeaderboardScore |
| ---: | ---: | ---: | ---: |
| 1 | 118.0 | 1.000 | 10.00 |
| 2 | 121.5 | 1.000 | 10.00 |
| 3 | 124.0 | 0.972 | 9.77 |
| 4 | 127.0 | 0.923 | 9.38 |
| 5 | 130.0 | 0.874 | 9.00 |
| 6 | 134.0 | 0.810 | 8.48 |
| 7 | 138.0 | 0.745 | 7.96 |
| 8 | 142.0 | 0.680 | 7.44 |
| 9 | 147.0 | 0.599 | 6.79 |
| 10 | 153.0 | 0.502 | 6.02 |
| 11 | 160.0 | 0.389 | 5.11 |
| 12 | 170.0 | 0.227 | 3.81 |
| 13 | 190.0 | 0.000 | 2.00 |
| 14 | 260.0 | 0.000 | 2.00 |

## Public-regulation wording and file layout

`LeaderboardScore` is calculated as a continuous number from 0 to 10 using private leaderboard results. Missing or invalid submit gives 0. Valid submits are normalized between robust private-score bounds: for an error metric, `BestBound = P10` and `WorstBound = P90`. Scores at or better than `BestBound` receive 10, scores at or worse than `WorstBound` receive 2, and intermediate results receive a proportional float score between 2 and 10.

For Obsidian-facing regulations, keep the main assessment file compact: formula in LaTeX, interpretation table, and a link to a separate numbered example note. Do not inline a long example table in the regulation once the formula is stable; use a sibling document such as `07 Leaderboard Example.md` and link it from both the regulation and project index.
