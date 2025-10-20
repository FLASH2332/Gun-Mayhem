# Gun Mayhem — AI (Fuzzy + GA)

This README documents only the AI side of the project: the plain fuzzy-logic bot and the genetic-algorithm–evolved fuzzy bot. It does not cover general game mechanics or C++ details.

## Architecture overview

- Core game (C++/SDL2) is exposed to Python via a compiled module `gunmayhem` (PyBind11).
- Python drives only the AI inputs; the engine keeps handling physics, collisions, rendering, and game loop.
- Three Python-facing wrappers are used during AI control:
	- `GameRunner`: start/stop game, step updates, render
	- `GameState`: read-only snapshot of players, bullets, and platforms (dicts)
	- `GameControl`: send per-player inputs (up/left/down/right/primaryFire/secondaryFire)

Data contract (simplified):
- Player state dict: `{ id, x, y, width, height, health, lives, facing_direction }`
- Actions dict produced by AI: `{ up, left, down, right, primaryFire, secondaryFire }` (booleans)

## Plain Fuzzy AI

Files:
- `fuzzy_ai.py` — Fuzzy controller (membership functions, rules, platform navigation, double-jump)
- `play_vs_ai.py` — Human (P1) vs Fuzzy AI (P2)

What it considers:
- Horizontal distance to enemy (close / medium / far)
- Vertical relation (below / same / above)
- Health levels (low / medium / high)
- Simple platform layout awareness (bottom platforms vs top platform)

Key mechanics:
- Membership functions (triangles/trapezoids) define ranges for distance, height-diff, and health.
- Rule evaluation produces intent (attack / reposition / retreat) and movement direction.
- Platform navigation chooses lateral targets and jump timing to reach the enemy’s level.
- Double jump is triggered by holding jump for a short window (~20 frames) when needed to climb 130 px gaps.

Outputs:
- Movement booleans and fire controls are returned as the actions dict each frame.

Quick try (human vs fuzzy):
```cmd
python play_vs_ai.py
```

## Fuzzy + GA (Evolvable Fuzzy)

Goal: keep the same fuzzy rules/structure, but evolve the numerical boundaries (membership function breakpoints and tactical thresholds) for better combat.

Files:
- `fuzzy_genome.py` — Encodes 21 tunable parameters (distances, health thresholds, height bands, aggression/shoot ranges, jump/ platform tolerances)
- `evolvable_fuzzy_ai.py` — Same behavior as `fuzzy_ai.py` but uses genome-provided values for all membership functions/thresholds
- `ga_trainer.py` — Headless bot-vs-bot training using GA; saves best genomes and stats
- `play_vs_evolved_ai.py` — Human vs the best evolved fuzzy bot

Genome (high level):
- Distance bands: close_max, medium_min/max, far_min
- Health bands: low_max, medium_min/max, high_min
- Height bands: below_max, same_range, above_min
- Tactics: aggression_threshold, secondary_fire_threshold
- Ranges: close/medium/far shoot distances
- Jumps: jump_frames (hold), fuzzy_jump_threshold
- Platforming: platform_y_tolerance, platform_jump_zone_width
- Safety: retreat_health_threshold, aggressive_distance

GA training loop:
1) Initialize a population of random genomes
2) Evaluate each bot by fighting a small random set of opponents (tournament)
3) Fitness: win score (bonus for faster wins, more health, remaining lives); draw small points; loss zero
4) Select top k (elites), then breed children via uniform crossover + per-gene mutation
5) Repeat for N generations; track and save the best

Defaults (tuned for fast iteration):
- Population: 5
- Matches per bot: 2 (random opponents)
- Elites: 2
- Generations: 3

Artifacts:
- Folder: `evolved_genomes/`
	- `best_genome.json` — current best
	- `best_genome_gen{N}.json` — snapshot per generation
	- `evolution_stats.json` — fitness over time

Run training (headless, quick):
```cmd
python ga_trainer.py
```

Play against the evolved fuzzy bot:
```cmd
python play_vs_evolved_ai.py
```

Notes on performance & windows:
- Training is headless (no render), but SDL may still create a window; it’s immediately cleaned up at match end.
- Holding jump for ~20 frames enables consistent double-jump climbs during platform navigation.

## Implementation notes / troubleshooting

- Ensure the Python module `gunmayhem` is built and importable (PyBind11). The scripts add DLL paths on Windows for SDL2/TTF.
- If `best_genome.json` is missing, the play scripts will fall back to random parameters.
- You can adjust the GA speed/quality trade-off by increasing population or generations once the pipeline looks good.

## File index (AI only)

- `fuzzy_ai.py` — Plain fuzzy controller
- `play_vs_ai.py` — Human vs plain fuzzy bot
- `fuzzy_genome.py` — Evolvable fuzzy parameters
- `evolvable_fuzzy_ai.py` — Fuzzy bot parameterized by genome
- `ga_trainer.py` — GA training for fuzzy parameters (saves to `evolved_genomes/`)
- `play_vs_evolved_ai.py` — Human vs evolved fuzzy bot
- `evolved_genomes/` — Best genomes and training stats

