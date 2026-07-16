# Herminator

An adaptive combat bot for [Battle LLM Robots](https://battlellmrobots.com).

## Strategy

Herminator is a direct-hybrid bot that closes distance while using ranged 
shots opportunistically. It always prioritizes facing the opponent before 
attacking (melee or ranged) — eliminating the critical bug that caused 
earlier versions to miss every melee hit when the opponent moved behind them.

**Priority per tick:**
1. Ranged — 15 damage is the best value; fire when aimed and in range.
2. Melee — 10 damage within 5 units, but only when facing the target.
3. Rotate — face the opponent before any action.
4. Move — close distance with wall avoidance.

**Key improvements over the original:**
- Removed broken `opponent_action` / `mirrored` tracking (the state dict 
  doesn't contain `opponent_action`, so this always evaluated as "mirrored"
  and triggered a retreat on first melee contact every time).
- Ranged at close range (15 vs 10 damage) — checked before melee so it 
  doesn't waste the better attack at point-blank range.
- Aim checked before melee — the original bot never rotated while in 
  melee range, making every attack miss once the opponent passed behind it.
- Uses `opponent_facing` to detect when the opponent's back is turned.

## Files

- `bot.py` — `decide(state, memory)` entry point (imports only `math`).
- `bot.yaml` — leaderboard metadata.

## Submission

Push to a **public** GitHub repo with `bot.py` and `bot.yaml` at root,
then register on battlellmrobots.com.