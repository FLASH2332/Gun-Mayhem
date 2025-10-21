"""
Watch a match: Fuzzy (evolved) vs Neural (evolved)
- Loads fuzzy genome from evolved_genomes/best_genome.json
- Loads neural genome from evolved_nn/best_genome.json
- Runs a headful game where both AIs fight each other
"""
import os
import sys
import time

# Add DLL paths
dll_paths = [
    r"C:\mingw64\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2-2.32.8\x86_64-w64-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2_ttf-2.24.0\x86_64-w64-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\build_pybind"
]

if sys.version_info >= (3, 8):
    for path in dll_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)

import gunmayhem
from fuzzy_genome import FuzzyGenome
from evolvable_fuzzy_ai import EvolvableFuzzyAI
from neural_genome import NeuralGenome
from neural_ai import NeuralAI


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    print("="*60)
    print("GUN MAYHEM - Fuzzy (Player1) vs Neural (Player2)")
    print("="*60)

    # Load genomes
    try:
        fuzzy_genome = FuzzyGenome.load("../evolved_genomes/best_genome.json")
        print("✓ Loaded fuzzy genome")
    except Exception as e:
        print(f"⚠ Using random fuzzy genome: {e}")
        fuzzy_genome = FuzzyGenome()

    try:
        nn_genome = NeuralGenome.load("../evolved_nn/best_genome.json")
        print("✓ Loaded neural genome")
    except Exception as e:
        print(f"⚠ Using random NN genome: {e}")
        nn_genome = NeuralGenome()

    fuzzy_ai = EvolvableFuzzyAI(fuzzy_genome)
    nn_ai = NeuralAI(nn_genome)

    input("\nPress ENTER to start the match...")

    game = gunmayhem.GameRunner()
    if not game.init_game("Gun Mayhem - Fuzzy vs NN"):
        print("Failed to initialize game!")
        return

    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()

    frame = 0
    kb_disabled = False

    print("Running match: Fuzzy (P1) vs NN (P2)")

    while game.is_running():
        game.handle_events()
        players = game_state.get_all_players()
        if len(players) >= 2:
            pids = list(players.keys())
            if not kb_disabled:
                # Disable keyboard for both AI players
                game_control.disable_keyboard_for_player(pids[0])
                game_control.disable_keyboard_for_player(pids[1])
                kb_disabled = True
            p1 = players[pids[0]]
            p2 = players[pids[1]]

            # Win checks
            if p2['lives'] <= 0 or p1['lives'] <= 0:
                winner = 'Fuzzy (P1)' if p2['lives'] <= 0 else 'Neural (P2)'
                print(f"\nWinner: {winner}")
                break

            # Decide actions
            a_fuzzy = fuzzy_ai.decide_action(p1, p2)
            a_nn = nn_ai.decide_action(p2, p1)

            # Apply controls
            game_control.set_player_movement(
                pids[0], bool(a_fuzzy['up']), bool(a_fuzzy['left']), bool(a_fuzzy['down']), bool(a_fuzzy['right']), bool(a_fuzzy['primaryFire']), bool(a_fuzzy['secondaryFire'])
            )
            game_control.set_player_movement(
                pids[1], bool(a_nn['up']), bool(a_nn['left']), bool(a_nn['down']), bool(a_nn['right']), bool(a_nn['primaryFire']), bool(a_nn['secondaryFire'])
            )
        game.update(0.0166)
        game.render()
        frame += 1
    print("\nMatch ended.")


if __name__ == "__main__":
    main()
