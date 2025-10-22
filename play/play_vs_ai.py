"""
Gun Mayhem - Fuzzy vs Fuzzy
- Player 1: Fuzzy AI
- Player 2: Fuzzy AI
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
    print("GUN MAYHEM - Fuzzy vs Fuzzy")
    print("=" * 60)
    print("Player 1: Fuzzy AI")
    print("Player 2: Fuzzy AI")
    print()
    print("Starting match...")
    
    # Initialize game
    game = gunmayhem.GameRunner()
    if not game.init_game("Gun Mayhem - Fuzzy vs Fuzzy"):
        print("Failed to initialize game!")
        return
    
    # Create wrappers
    game_state = gunmayhem.GameState()
    game_control = gunmayhem.GameControl()
    
    # Initialize separate AI instances (avoid shared jump/hold state)
    ai1 = FuzzyAI() if FUZZY_AVAILABLE else SimpleFuzzyAI()
    ai2 = FuzzyAI() if FUZZY_AVAILABLE else SimpleFuzzyAI()
    
    frame_count = 0
    last_print = time.time()
    
    print("Game running! Both players are AI-controlled.")
    
    # Disable keyboard for both AI players once
    kb_disabled = False
    
    # Game loop
    while game.is_running():
        game.handle_events()
        
        # Get current game state
        players = game_state.get_all_players()
        
        # Control AI player if there are 2 players
        if len(players) >= 2:
            player_ids = list(players.keys())
            
            # Disable keyboard for both AI players (only once)
            if not kb_disabled:
                game_control.disable_keyboard_for_player(player_ids[0])
                game_control.disable_keyboard_for_player(player_ids[1])
                kb_disabled = True
                print(f"Fuzzy AIs taking control of {player_ids[0]} and {player_ids[1]}")
            
            # Assume player1 is human, player2 is AI
            # You can adjust this based on actual player IDs
            if len(player_ids) >= 2:
                player1_state = players[player_ids[0]]
                player2_state = players[player_ids[1]]
                
                # Win checks
                if player1_state['lives'] <= 0 or player2_state['lives'] <= 0:
                    winner = 'AI 2 (P2)' if player1_state['lives'] <= 0 else 'AI 1 (P1)'
                    print(f"\nWinner: {winner}")
                    break

                # AI decides actions (separate instances for each player)
                ai_actions1 = ai1.decide_action(player1_state, player2_state)
                ai_actions2 = ai2.decide_action(player2_state, player1_state)
                
                # Enhanced debug output
                if frame_count % 60 == 0:  # Every second at 60 FPS
                    distance = abs(player2_state['x'] - player1_state['x'])
                    height_diff = player2_state['y'] - player1_state['y']
                    
                    # Determine levels
                    ai_level = 'TOP' if abs(player2_state['y'] - 300) < 100 else 'BOTTOM'
                    human_level = 'TOP' if abs(player1_state['y'] - 300) < 100 else 'BOTTOM'
                    
                    print(f"\n[AI DECISION] Frame {frame_count}")
                    print(f"  Levels: AI2={ai_level} ({player2_state['y']:.0f}), AI1={human_level} ({player1_state['y']:.0f})")
                    print(f"  Distance: {distance:.0f}px, Height Diff: {height_diff:.0f}px")
                    print(f"  AI1 Actions: Jump={ai_actions1['up']}, Left={ai_actions1['left']}, Right={ai_actions1['right']}, Shoot={ai_actions1['primaryFire']}")
                    print(f"  AI2 Actions: Jump={ai_actions2['up']}, Left={ai_actions2['left']}, Right={ai_actions2['right']}, Shoot={ai_actions2['primaryFire']}")
                
                # Send AI1 controls to player 1 (positional arguments required)
                game_control.set_player_movement(
                    player_ids[0],
                    bool(ai_actions1['up']),
                    bool(ai_actions1['left']),
                    bool(ai_actions1['down']),
                    bool(ai_actions1['right']),
                    bool(ai_actions1['primaryFire']),
                    bool(ai_actions1['secondaryFire'])
                )

                # Send AI2 controls to player 2 (positional arguments required)
                game_control.set_player_movement(
                    player_ids[1],
                    bool(ai_actions2['up']),
                    bool(ai_actions2['left']),
                    bool(ai_actions2['down']),
                    bool(ai_actions2['right']),
                    bool(ai_actions2['primaryFire']),
                    bool(ai_actions2['secondaryFire'])
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
            for idx, (player_id, p) in enumerate(players.items()):
                label = "AI1" if idx == 0 else "AI2"
                print(f"  [{label}] {player_id}: HP={p['health']:5.1f}, Lives={p['lives']}, Pos=({p['x']:6.1f}, {p['y']:6.1f})")
            
            last_print = time.time()
        
        time.sleep(0.016)  # ~60 FPS
    
    print("\nGame ended!")


if __name__ == "__main__":
    main()
