"""
Records your gameplay for 10 seconds and saves it as 'my_recording.json'.
You are Player 1 (P1) and you're fighting a dummy AI (P2).

HOW TO USE:
1. Run this script.
2. The game window will open.
3. You have 3 seconds to get ready.
4. When you see "RECORDING...", play your best 10-second sequence!
5. The game will close and save 'my_recording.json'.
"""
import os
import sys
import time
import json
import keyboard  # pip install keyboard
import numpy as np

# Add DLL paths
dll_paths = [
    r"C:\mingw64\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2-2.32.8\x86_64-w664-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2_ttf-2.24.0\x86_64-w664-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\build_pybind"
]
if sys.version_info >= (3, 8):
    for path in dll_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)

import gunmayhem
from fuzzy.fuzzy_ai import SimpleFuzzyAI # Opponent bot

# --- Configuration ---
RECORD_DURATION_SEC = 10
FPS = 60
TOTAL_FRAMES = RECORD_DURATION_SEC * FPS
OUTPUT_FILE = "my_recording.json"

# P1 controls (from your gameConfig.json)
CONTROLS = {
    'w': 'up',
    'a': 'left',
    's': 'down',
    'd': 'right',
    't': 'primaryFire',
    'y': 'secondaryFire'
}
# ---

def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    print("="*60)
    print(f"GAMEPLAY RECORDER (10 seconds)")
    print("="*60)
    print("You are Player 1. Play against the AI.")
    print("Get ready, recording will start in 3 seconds...")

    game = gunmayhem.GameRunner()
    if not game.init_game("RECORDING YOUR GAMEPLAY"):
        print("Failed to initialize game!")
        return

    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()
    
    # Simple AI for Player 2
    ai = SimpleFuzzyAI() 
    p1_id, p2_id = None, None
    ai_keyboard_disabled = False

    recorded_actions = []
    
    start_time = time.time()
    recording_started = False
    
    try:
        frame_count = 0
        while game.is_running():
            game.handle_events()
            
            # Get player states
            players = game_state.get_all_players()
            if len(players) < 2:
                game.update(0.0166)
                game.render()
                continue

            if p1_id is None:
                p1_id, p2_id = list(players.keys())[:2]
            
            if not ai_keyboard_disabled:
                # We are P1, so disable AI for P2
                game_control.disable_keyboard_for_player(p2_id)
                ai_keyboard_disabled = True

            p1_state = players.get(p1_id)
            p2_state = players.get(p2_id)
            
            if not p1_state or not p2_state:
                continue

            # --- Handle AI (P2) ---
            ai_actions = ai.decide_action(p2_state, p1_state)
            # game_control.set_player_movement(
            #     p2_id, 
            #     bool(ai_actions['up']), bool(ai_actions['left']),
            #     bool(ai_actions['down']), bool(ai_actions['right']),
            #     bool(ai_actions['primaryFire']), bool(ai_actions['secondaryFire'])
            # )

            # --- Handle Recording (P1) ---
            if not recording_started and time.time() - start_time > 3.0:
                print("RECORDING... (10 seconds)")
                recording_started = True
                frame_count = 0

            if recording_started:
                if frame_count >= TOTAL_FRAMES:
                    print("Recording finished.")
                    break # End game loop

                # Read keyboard state
                human_action = {
                    'up': keyboard.is_pressed('up arrow'),
                    'left': keyboard.is_pressed('left arrow'),
                    'down': keyboard.is_pressed('down arrow'),
                    'right': keyboard.is_pressed('right arrow'),
                    'primaryFire': keyboard.is_pressed('.'),
                    'secondaryFire': keyboard.is_pressed(',')
                }
                recorded_actions.append(human_action)
                frame_count += 1
            
            # Update and render
            game.update(0.0166)
            game.render()
            time.sleep(0.016)

    except KeyboardInterrupt:
        print("\nRecording stopped early.")
    finally:
        game.quit()
        if recorded_actions:
            with open(f"../{OUTPUT_FILE}", 'w') as f:
                json.dump(recorded_actions, f, indent=2)
            print(f"Successfully saved {len(recorded_actions)} frames to {OUTPUT_FILE}")
        os.chdir(project_root)

if __name__ == "__main__":
    main()