"""
Play against the evolved MARL (PPO) bot.
- Player 1: Human controlled
- Player 2: MARL AI
"""
import os
import sys
import time
import numpy as np
import gym

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
from stable_baselines3 import PPO
from feature_extraction import get_observation # Use the same feature extractor

MODEL_PATH = "models_marl/ppo_gunmayhem_marl.zip"

def _convert_action(action_array) -> Dict:
    """Converts MultiBinary array [0,1,0,1,1,0] to action dict."""
    return {
        'up': bool(action_array[0]),
        'left': bool(action_array[1]),
        'down': bool(action_array[2]),
        'right': bool(action_array[3]),
        'primaryFire': bool(action_array[4]),
        'secondaryFire': bool(action_array[5]),
    }

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    print("="*60)
    print("GUN MAYHEM - Human vs MARL AI")
    print("="*60)

    # Load trained model
    try:
        model = PPO.load(MODEL_PATH)
        print(f"✓ Loaded trained MARL model from {MODEL_PATH}")
    except Exception as e:
        print(f"⚠ Could not load model: {e}")
        print("  Please run marl_trainer.py first.")
        return

    input("\nPress ENTER to start the match...")

    game = gunmayhem.GameRunner()
    if not game.init_game("Gun Mayhem - Human vs MARL AI"):
        print("Failed to initialize game!")
        return

    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()

    ai_keyboard_disabled = False
    p1_id, p2_id = None, None

    print("Running match: Human (P1) vs MARL AI (P2)")

    try:
        while game.is_running():
            game.handle_events()
            players = game_state.get_all_players()
            
            if len(players) >= 2:
                if p1_id is None:
                    p1_id, p2_id = list(players.keys())[:2]
                
                if not ai_keyboard_disabled:
                    # Disable keyboard ONLY for AI player (P2)
                    game_control.disable_keyboard_for_player(p2_id)
                    ai_keyboard_disabled = True
                    print(f"MARL AI taking control of {p2_id}")

                p1_state = players.get(p1_id)
                p2_state = players.get(p2_id)
                
                if not p1_state or not p2_state:
                    continue # Wait for states to be valid
                    
                # Check win
                if p1_state['lives'] <= 0 or p2_state['lives'] <= 0:
                    winner = "MARL AI (P2)" if p1_state['lives'] <= 0 else "Human (P1)"
                    print(f"\nGAME OVER! Winner: {winner}")
                    break
                
                # --- AI Decision ---
                # 1. Get observation for AI (P2 vs P1)
                obs_p2 = get_observation(p2_state, p1_state)
                
                # 2. Predict action
                action_p2_array, _ = model.predict(obs_p2, deterministic=True)
                
                # 3. Convert and apply action
                action_p2_dict = _convert_action(action_p2_array)
                game_control.set_player_movement(p2_id, **action_p2_dict)

            # Update and render
            game.update(0.0166)
            game.render()
            time.sleep(0.016) # ~60 FPS

    except KeyboardInterrupt:
        print("\nMatch stopped by user.")
    finally:
        print("Quitting game...")
        game.quit()

if __name__ == "__main__":
    main()