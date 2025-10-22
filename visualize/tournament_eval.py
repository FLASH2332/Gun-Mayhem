"""
Tournament evaluation among three bots:
- fuzzy (baseline FuzzyAI)
- fuzzy_ga (EvolvableFuzzyAI using evolved_genomes/best_genome.json)
- marl (SB3 PPO policy from models_marl/best_opponent.zip)

Each pair plays N matches (default 5) headless. Results are saved to visualize/tournament_results/ as JSON.

Run:
    python -u "visualize/tournament_eval.py" --matches 5 --show-summary
"""
import os
import sys
import time
import json
import math
from datetime import datetime
from typing import Dict, Tuple

# Ensure project root on path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# DLL dirs for SDL2 and pybind
dll_paths = [
    r"C:\mingw64\bin",
    os.path.join(PROJECT_ROOT, "libs", "SDL2-2.32.8", "x86_64-w64-mingw32", "bin"),
    os.path.join(PROJECT_ROOT, "libs", "SDL2_ttf-2.24.0", "x86_64-w64-mingw32", "bin"),
    os.path.join(PROJECT_ROOT, "build_pybind"),
]
if sys.version_info >= (3, 8):
    for p in dll_paths:
        if os.path.exists(p):
            os.add_dll_directory(p)

import argparse
import gunmayhem

from fuzzy.fuzzy_ai import FuzzyAI, SimpleFuzzyAI, FUZZY_AVAILABLE
from fuzzy.evolvable_fuzzy_ai import EvolvableFuzzyAI
from ga.fuzzy_genome import FuzzyGenome
from stable_baselines3 import PPO
from feature_extraction import get_observation


def make_ai(kind: str):
    kind = kind.lower()
    if kind == "fuzzy":
        return FuzzyAI() if FUZZY_AVAILABLE else SimpleFuzzyAI()
    if kind == "fuzzy_ga":
        # Try to load evolved genome
        path = os.path.join(PROJECT_ROOT, "evolved_genomes", "best_genome.json")
        try:
            g = FuzzyGenome.load(path)
        except Exception:
            g = FuzzyGenome()
        return EvolvableFuzzyAI(g)
    if kind == "marl":
        model_path = os.path.join(PROJECT_ROOT, "models_marl", "best_opponent")
        try:
            model = PPO.load(model_path)
        except Exception:
            model = None

        class MarlPolicyAI:
            def __init__(self, m):
                self.model = m
            def _convert_action(self, arr) -> Dict:
                return {
                    'up': bool(arr[0]),
                    'left': bool(arr[1]),
                    'down': bool(arr[2]),
                    'right': bool(arr[3]),
                    'primaryFire': bool(arr[4]),
                    'secondaryFire': bool(arr[5]),
                }
            def decide_action(self, me: Dict, enemy: Dict) -> Dict:
                if self.model is None:
                    # Fallback: passive actions
                    return {'up': False, 'left': False, 'down': False, 'right': False, 'primaryFire': False, 'secondaryFire': False}
                obs = get_observation(me, enemy)
                action_arr, _ = self.model.predict(obs, deterministic=True)
                return self._convert_action(action_arr)

        return MarlPolicyAI(model)
    raise ValueError(f"Unknown AI kind: {kind}")


def play_match(ai1, ai2, max_frames=1200, render=False) -> Tuple[str, Dict]:
    """Run one headless match between two AIs. Returns (winner, stats)."""
    build_dir = os.path.join(PROJECT_ROOT, 'build')
    os.makedirs(build_dir, exist_ok=True)
    original_dir = os.getcwd()
    os.chdir(build_dir)
    try:
        game = gunmayhem.GameRunner()
        if not game.init_game("Tournament Match"):
            os.chdir(original_dir)
            return 'draw', {}
        game_state = gunmayhem.GameState()
        game_control = gunmayhem.GameControl()

        frame = 0
        disabled = False
        total_distance = 0.0
        samples = 0
        shots1 = 0
        shots2 = 0

        while game.is_running() and frame < max_frames:
            game.handle_events()
            players = game_state.get_all_players()
            if len(players) >= 2:
                pids = list(players.keys())
                if not disabled:
                    # Disable keyboard for both AI players
                    game_control.disable_keyboard_for_player(pids[0])
                    game_control.disable_keyboard_for_player(pids[1])
                    disabled = True
                p1 = players[pids[0]]
                p2 = players[pids[1]]

                # win checks
                if p2['lives'] <= 0:
                    game.quit(); os.chdir(original_dir)
                    return 'ai1', {
                        'frames': frame,
                        'p1_health': p1['health'],
                        'p2_health': p2['health'],
                        'p1_lives': p1['lives'],
                        'p2_lives': p2['lives'],
                    }
                if p1['lives'] <= 0:
                    game.quit(); os.chdir(original_dir)
                    return 'ai2', {
                        'frames': frame,
                        'p1_health': p1['health'],
                        'p2_health': p2['health'],
                        'p1_lives': p1['lives'],
                        'p2_lives': p2['lives'],
                    }

                # accumulate distance metric
                dx = p2['x'] - p1['x']
                dy = p2['y'] - p1['y']
                total_distance += math.hypot(dx, dy)
                samples += 1

                # Decide actions
                a1 = ai1.decide_action(p1, p2)
                a2 = ai2.decide_action(p2, p1)
                if a1.get('primaryFire'): shots1 += 1
                if a2.get('primaryFire'): shots2 += 1

                # Apply controls (positional args required)
                game_control.set_player_movement(
                    pids[0],
                    bool(a1['up']), bool(a1['left']), bool(a1['down']), bool(a1['right']),
                    bool(a1['primaryFire']), bool(a1['secondaryFire'])
                )
                game_control.set_player_movement(
                    pids[1],
                    bool(a2['up']), bool(a2['left']), bool(a2['down']), bool(a2['right']),
                    bool(a2['primaryFire']), bool(a2['secondaryFire'])
                )

            game.update(0.0166)
            if render:
                game.render()
            frame += 1

        # timeout -> apply tie-breakers before declaring draw
        avg_dist = (total_distance / samples) if samples else 0.0
        out = {
            'frames': frame,
            'avg_distance': avg_dist,
            'p1_health': p1['health'] if samples else 0.0,
            'p2_health': p2['health'] if samples else 0.0,
            'p1_lives': p1['lives'] if samples else 0,
            'p2_lives': p2['lives'] if samples else 0,
            'shots1': shots1,
            'shots2': shots2,
        }
        # Tie-breaker order: lives > health > shots; otherwise draw
        if out['p1_lives'] > out['p2_lives']:
            winner = 'ai1'
        elif out['p2_lives'] > out['p1_lives']:
            winner = 'ai2'
        elif out['p1_health'] > out['p2_health'] + 0.5:
            winner = 'ai1'
        elif out['p2_health'] > out['p1_health'] + 0.5:
            winner = 'ai2'
        elif out['shots1'] > out['shots2'] + 2:
            winner = 'ai1'
        elif out['shots2'] > out['shots1'] + 2:
            winner = 'ai2'
        else:
            winner = 'draw'
        game.quit(); os.chdir(original_dir)
        return winner, out
    except Exception as e:
        try:
            game.quit()
        except Exception:
            pass
        os.chdir(original_dir)
        return 'draw', {'error': str(e)}


def run_pair(name1: str, name2: str, matches: int, render=False, alternate_sides: bool = True):
    ai1 = make_ai(name1)
    ai2 = make_ai(name2)
    results = []
    p1_wins = p2_wins = draws = 0
    for i in range(matches):
        # Alternate sides by swapping AI roles every other match (unless disabled)
        if (i % 2 == 0) or (not alternate_sides):
            # ai1 takes Player1 side, ai2 takes Player2 side
            winner, stats = play_match(ai1, ai2, render=render)
            winner_side = 'p1' if winner == 'ai1' else ('p2' if winner == 'ai2' else 'none')
            mapped_winner = winner  # already in identity space (ai1 vs ai2)
            p1_ai_id, p2_ai_id = 'ai1', 'ai2'
            p1_name, p2_name = name1, name2
        else:
            # ai2 takes Player1 side, ai1 takes Player2 side
            winner, stats = play_match(ai2, ai1, render=render)
            winner_side = 'p1' if winner == 'ai1' else ('p2' if winner == 'ai2' else 'none')
            # Map back to identity space: match-level 'ai1' corresponds to identity 'ai2' here
            if winner == 'ai1':
                mapped_winner = 'ai2'
            elif winner == 'ai2':
                mapped_winner = 'ai1'
            else:
                mapped_winner = 'draw'
            p1_ai_id, p2_ai_id = 'ai2', 'ai1'
            p1_name, p2_name = name2, name1

        if mapped_winner == 'ai1': p1_wins += 1
        elif mapped_winner == 'ai2': p2_wins += 1
        else: draws += 1
        results.append({
            'match': i + 1,
            'winner': mapped_winner,
            'winner_name': (name1 if mapped_winner == 'ai1' else (name2 if mapped_winner == 'ai2' else 'draw')),
            'winner_side': winner_side,
            'p1_ai': p1_ai_id,
            'p2_ai': p2_ai_id,
            'p1_name': p1_name,
            'p2_name': p2_name,
            'stats': stats,
        })
    return {
        'pair': f"{name1}_vs_{name2}",
        'p1': name1,
        'p2': name2,
        'results': results,
        'summary': {
            'p1_wins': p1_wins,
            'p2_wins': p2_wins,
            'draws': draws,
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Run tournament among fuzzy, fuzzy_ga, nn")
    parser.add_argument('--matches', type=int, default=5, help='Matches per pair')
    parser.add_argument('--render', action='store_true', help='Render matches (slower)')
    parser.add_argument('--show-summary', action='store_true', help='Print summary to console')
    parser.add_argument('--fixed-sides', action='store_true', help='Do not alternate sides between matches (ai1 always P1)')
    args = parser.parse_args()

    pairs = [
        ("fuzzy", "fuzzy_ga"),
        ("fuzzy", "marl"),
        ("fuzzy_ga", "marl"),
    ]

    all_results = {
        'timestamp': datetime.now().isoformat(timespec='seconds'),
        'matches_per_pair': args.matches,
        'alternate_sides': (not args.fixed_sides),
        'pairs': []
    }

    print("\n=== Running tournament ===")
    for p1, p2 in pairs:
        print(f"- {p1} vs {p2} ({args.matches} matches)")
        res = run_pair(p1, p2, args.matches, render=args.render, alternate_sides=(not args.fixed_sides))
        all_results['pairs'].append(res)

    # Save results
    out_dir = os.path.join(PROJECT_ROOT, 'visualize', 'tournament_results')
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"tournament_{int(time.time())}.json")
    with open(out_file, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"Saved results to: {out_file}")

    if args.show_summary:
        print("\n=== Summary ===")
        for pair in all_results['pairs']:
            s = pair['summary']
            print(f"{pair['pair']}: {s['p1_wins']}-{s['p2_wins']} (draws {s['draws']})")


if __name__ == '__main__':
    main()
