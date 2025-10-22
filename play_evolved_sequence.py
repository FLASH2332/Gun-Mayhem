"""
Plays the best evolved sequence bot (P1) against your
original recording (P2) with rendering, so you can watch.
"""
import os
import sys
import time
import json
from typing import Dict

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
from sequence_genome import SequenceGenome, TOTAL_FRAMES

RECORDING_FILE = "my_recording.json"
EVOLVED_GENOME = "evolved_sequence/best_genome.json"


def _translate_genome_to_action(int_dict: Dict[str, int]) -> Dict[str, bool]:
    """
    Converts the 3-integer genome chunk into the 6-boolean
    action dictionary required by the game.
    """
    h = int_dict['horizontal']
    v = int_dict['vertical']
    s = int_dict['shoot']

    return {
        'up': (v == 0),
        'left': (h == 0),
        'down': (v == 1),
        'right': (h == 1),
        'primaryFire': (s == 0),
        'secondaryFire': (s == 1)
    }


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    print("="*60)
    print("EVOLVED BOT (P1) vs YOUR RECORDING (P2)")
    print("="*60)
    
    # Load genome
    try:
        genome = SequenceGenome.load(f"../{EVOLVED_GENOME}")
        print(f"✓ Loaded evolved genome: {EVOLVED_GENOME}")
    except Exception as e:
        print(f"Error loading genome: {e}")
        return

    # Load recording
    try:
        with open(f"../{RECORDING_FILE}", 'r') as f:
            recording = json.load(f)
        print(f"✓ Loaded recording: {RECORDING_FILE}")
    except Exception as e:
        print(f"Error loading recording: {e}")
        return
        
    input("\nPress ENTER to start the match...")

    game = gunmayhem.GameRunner()
    if not game.init_game("Evolved GA vs Human Recording"):
        print("Failed to initialize game!")
        return

    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()
    p1_id, p2_id = None, None

    try:
        for frame in range(TOTAL_FRAMES):
            if not game.is_running():
                break
                
            game.handle_events()
            players = game_state.get_all_players()
            
            if len(players) < 2:
                game.update(0.0166)
                game.render()
                continue

            if p1_id is None:
                p1_id, p2_id = list(players.keys())[:2]
                game_control.disable_keyboard_for_player(p1_id)
                game_control.disable_keyboard_for_player(p2_id)

            p1_state = players.get(p1_id)
            p2_state = players.get(p2_id)

            if not p1_state or not p2_state or p1_state['lives'] <= 0 or p2_state['lives'] <= 0:
                break
            
            # --- ACTION TRANSLATION ---
            action_p1_int = genome.get_action_for_frame(frame)
            action_p1_bool = _translate_genome_to_action(action_p1_int)
            action_p2 = recording[frame]
            
            # Apply actions
            game_control.set_player_movement(
                p1_id, action_p1_bool['up'], action_p1_bool['left'], action_p1_bool['down'],
                action_p1_bool['right'], action_p1_bool['primaryFire'], action_p1_bool['secondaryFire']
            )
            game_control.set_player_movement(
                p2_id, action_p2['up'], action_p2['left'], action_p2['down'],
                action_p2['right'], action_p2['primaryFire'], action_p2['secondaryFire']
            )
            
            game.update(0.0166)
            game.render()
            time.sleep(0.016) # ~60 FPS
            
        print("Match finished.")
        # Hold the final screen for 3 seconds
        time.sleep(3.0)

    except KeyboardInterrupt:
        print("\nMatch stopped.")
    finally:
        game.quit()
        os.chdir(project_root)

if __name__ == "__main__":
    main()