"""
Gun Mayhem with Fuzzy AI
- Player 1: Human controlled (WASD + Space to shoot)
- Player 2: AI controlled with fuzzy logic
"""

import os
import sys
import time

# Ensure project root is on sys.path when running from this subfolder
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

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
from fuzzy.fuzzy_ai import FuzzyAI, SimpleFuzzyAI, FUZZY_AVAILABLE


def main():
    # Change to build directory at repo root so ../assets resolves correctly
    build_dir = os.path.join(PROJECT_ROOT, 'build')
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    os.chdir(build_dir)
    
    print("=" * 60)
    print("GUN MAYHEM - Human vs Fuzzy AI")
    print("=" * 60)
    print("Player 1: YOU (Controlled by keyboard in game)")
    print("Player 2: FUZZY AI (Controlled by Python)")
    print()
    print("Starting game...")
    
    # Initialize game
    game = gunmayhem.GameRunner()
    if not game.init_game("Gun Mayhem - Human vs AI"):
        print("Failed to initialize game!")
        return
    
    # Create wrappers
    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()
    
    # Initialize AI
    ai = FuzzyAI() if FUZZY_AVAILABLE else SimpleFuzzyAI()
    
    frame_count = 0
    last_print = time.time()
    
    print("Game running! Play with the keyboard, AI will control Player 2")
    
    # Flag to track if we've disabled keyboard for AI player
    ai_keyboard_disabled = False
    
    # Game loop
    while game.is_running():
        game.handle_events()
        
        # Get current game state
        players = game_state.get_all_players()
        
        # Control AI player if there are 2 players
        if len(players) >= 2:
            player_ids = list(players.keys())
            
            # Disable keyboard for AI player (only once)
            if not ai_keyboard_disabled:
                game_control.disable_keyboard_for_player(player_ids[1])
                ai_keyboard_disabled = True
                print(f"AI taking control of {player_ids[1]}")
            
            # Assume player1 is human, player2 is AI
            # You can adjust this based on actual player IDs
            if len(player_ids) >= 2:
                player1_state = players[player_ids[0]]
                player2_state = players[player_ids[1]]
                
                # AI decides actions
                ai_actions = ai.decide_action(player2_state, player1_state)
                
                # Enhanced debug output
                if frame_count % 60 == 0:  # Every second at 60 FPS
                    distance = abs(player2_state['x'] - player1_state['x'])
                    height_diff = player2_state['y'] - player1_state['y']
                    
                    # Determine levels
                    ai_level = 'TOP' if abs(player2_state['y'] - 300) < 100 else 'BOTTOM'
                    human_level = 'TOP' if abs(player1_state['y'] - 300) < 100 else 'BOTTOM'
                    
                    print(f"\n[AI DECISION] Frame {frame_count}")
                    print(f"  Levels: AI={ai_level} ({player2_state['y']:.0f}), Human={human_level} ({player1_state['y']:.0f})")
                    print(f"  Distance: {distance:.0f}px, Height Diff: {height_diff:.0f}px")
                    print(f"  Actions: Jump={ai_actions['up']}, Left={ai_actions['left']}, Right={ai_actions['right']}, Shoot={ai_actions['primaryFire']}")
                
                # Send AI controls to player 2 (must use positional arguments)
                game_control.set_player_movement(
                    player_ids[1],                          # player ID
                    bool(ai_actions['up']),                 # up
                    bool(ai_actions['left']),               # left
                    bool(ai_actions['down']),               # down
                    bool(ai_actions['right']),              # right
                    bool(ai_actions['primaryFire']),        # primaryFire
                    bool(ai_actions['secondaryFire'])       # secondaryFire
                )
        
        # Update and render
        game.update(0.0166)
        game.render()
        
        # Print stats every second
        frame_count += 1
        if time.time() - last_print > 1.0:
            bullets = game_state.get_all_bullets()
            
            print(f"\n[GAME STATE] Frame {frame_count}")
            print(f"  Players: {len(players)}, Bullets: {len(bullets)}")
            for player_id, p in players.items():
                player_type = "HUMAN" if player_id == list(players.keys())[0] else "AI   "
                print(f"  [{player_type}] {player_id}: HP={p['health']:5.1f}, Lives={p['lives']}, Pos=({p['x']:6.1f}, {p['y']:6.1f})")
            
            last_print = time.time()
        
        time.sleep(0.016)  # ~60 FPS
    
    print("\nGame ended!")


if __name__ == "__main__":
    main()
