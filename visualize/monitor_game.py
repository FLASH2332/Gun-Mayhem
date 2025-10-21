"""
Monitor Gun Mayhem game state in real-time
Run this WHILE the game is running to see live game data
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

# Ensure project root on path when running this module directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import gunmayhem

def main():
    print("Gun Mayhem Game Monitor")
    print("=" * 50)
    print("Start the game and enter PlayState (start playing)")
    print("This script will display live game data")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    game_state = gunmayhem.GameState()
    
    while True:
        try:
            # Get game info
            info = game_state.get_game_info()
            
            if not info['is_running']:
                print("\rWaiting for game to start...", end='', flush=True)
                time.sleep(0.5)
                continue
            
            # Get all game objects
            players = game_state.get_all_players()
            bullets = game_state.get_all_bullets()
            platforms = game_state.get_all_platforms()
            
            # Clear screen (simple version)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("=== GUN MAYHEM - LIVE GAME STATE ===")
            print(f"Screen: {info['screen_width']}x{info['screen_height']}")
            print(f"Running: {info['is_running']}")
            print()
            
            # Display players
            print(f"PLAYERS ({len(players)}):")
            for player_id, p in players.items():
                print(f"  {player_id}:")
                print(f"    Health: {p['health']}/100  Lives: {p['lives']}")
                print(f"    Position: ({p['x']:.1f}, {p['y']:.1f})")
                print(f"    Facing: {'←LEFT' if p['facing_direction']==0 else 'RIGHT→'}")
            
            # Display bullets
            print(f"\nBULLETS ({len(bullets)}):")
            if len(bullets) > 0:
                for bullet_id, b in bullets.items():
                    print(f"  {bullet_id}: Owner={b['owner_id']}, Pos=({b['x']:.1f}, {b['y']:.1f}), Damage={b['damage']}")
            else:
                print("  None")
            
            # Display platforms
            print(f"\nPLATFORMS ({len(platforms)}):")
            for platform_id, plat in platforms.items():
                print(f"  {platform_id}: ({plat['x']:.1f}, {plat['y']:.1f}) - {plat['width']:.1f}x{plat['height']:.1f}")
            
            time.sleep(0.1)  # Update 10 times per second
            
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
            break
        except Exception as e:
            print(f"\nError: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
