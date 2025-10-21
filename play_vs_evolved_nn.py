"""
Play against the evolved NN bot.
Loads evolved_nn/best_genome.json and runs a human vs AI match.
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
from neural_genome import NeuralGenome
from neural_ai import NeuralAI


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    print("="*60)
    print("GUN MAYHEM - Human vs EVOLVED NN AI")
    print("="*60)

    # Load genome
    try:
        genome = NeuralGenome.load("../evolved_nn/best_genome.json")
        print("\n✓ Loaded evolved NN genome!")
        print(genome.summary())
    except Exception as e:
        print(f"\n⚠ Could not load evolved NN genome: {e}")
        print("  Starting with a random genome.")
        genome = NeuralGenome()

    input("\nPress ENTER to start...")

    # Init game
    game = gunmayhem.GameRunner()
    if not game.init_game("Gun Mayhem - vs Evolved NN AI"):
        print("Failed to initialize game!")
        return

    ai = NeuralAI(genome)
    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()

    frame = 0
    ai_keyboard_disabled = False

    print("Game running! You are Player 1.")

    while game.is_running():
        game.handle_events()
        players = game_state.get_all_players()
        if len(players) >= 2:
            pids = list(players.keys())
            if not ai_keyboard_disabled:
                game_control.disable_keyboard_for_player(pids[1])
                ai_keyboard_disabled = True
                print(f"NN AI taking control of {pids[1]}")
            p1 = players[pids[0]]
            p2 = players[pids[1]]
            actions = ai.decide_action(p2, p1)
            game_control.set_player_movement(
                pids[1],
                bool(actions['up']), bool(actions['left']), bool(actions['down']), bool(actions['right']),
                bool(actions['primaryFire']), bool(actions['secondaryFire'])
            )
        game.update(0.0166)
        game.render()
        frame += 1
    print("\nGame ended!")


if __name__ == "__main__":
    main()
