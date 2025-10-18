"""
Gun Mayhem with Fuzzy AI
- Player 1: Human controlled (WASD + Space to shoot)
- Player 2: AI controlled with fuzzy logic
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
import numpy as np

# Try to import scikit-fuzzy (optional)
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    FUZZY_AVAILABLE = True
except ImportError:
    print("WARNING: scikit-fuzzy not installed. Using simple AI instead.")
    print("Install with: pip install scikit-fuzzy")
    FUZZY_AVAILABLE = False


class SimpleFuzzyAI:
    """Simple rule-based AI if scikit-fuzzy is not available"""
    def decide_action(self, ai_state, enemy_state):
        distance = abs(ai_state['x'] - enemy_state['x'])
        health_ratio = ai_state['health'] / 100.0
        
        # Simple rules
        should_jump = ai_state['y'] > enemy_state['y'] + 50
        move_towards_enemy = ai_state['x'] < enemy_state['x']
        should_shoot = distance < 400
        aggressive = health_ratio > 0.5
        
        return {
            'up': should_jump,
            'left': not move_towards_enemy,
            'right': move_towards_enemy,
            'down': False,
            'primaryFire': should_shoot and aggressive,
            'secondaryFire': False
        }


class FuzzyAI:
    """Fuzzy logic AI controller using scikit-fuzzy"""
    def __init__(self):
        if not FUZZY_AVAILABLE:
            return
        
        # Define fuzzy variables
        self.distance = ctrl.Antecedent(np.arange(0, 1001, 1), 'distance')
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
        self.enemy_health = ctrl.Antecedent(np.arange(0, 101, 1), 'enemy_health')
        self.height_diff = ctrl.Antecedent(np.arange(-500, 501, 1), 'height_diff')
        
        # Outputs
        self.aggression = ctrl.Consequent(np.arange(0, 101, 1), 'aggression')
        self.should_jump = ctrl.Consequent(np.arange(0, 101, 1), 'should_jump')
        
        # Membership functions
        self.distance['close'] = fuzz.trimf(self.distance.universe, [0, 0, 300])
        self.distance['medium'] = fuzz.trimf(self.distance.universe, [200, 500, 800])
        self.distance['far'] = fuzz.trimf(self.distance.universe, [700, 1000, 1000])
        
        self.health['low'] = fuzz.trimf(self.health.universe, [0, 0, 40])
        self.health['medium'] = fuzz.trimf(self.health.universe, [30, 50, 70])
        self.health['high'] = fuzz.trimf(self.health.universe, [60, 100, 100])
        
        self.enemy_health['low'] = fuzz.trimf(self.enemy_health.universe, [0, 0, 40])
        self.enemy_health['medium'] = fuzz.trimf(self.enemy_health.universe, [30, 50, 70])
        self.enemy_health['high'] = fuzz.trimf(self.enemy_health.universe, [60, 100, 100])
        
        self.height_diff['below'] = fuzz.trimf(self.height_diff.universe, [-500, -500, -50])
        self.height_diff['same'] = fuzz.trimf(self.height_diff.universe, [-100, 0, 100])
        self.height_diff['above'] = fuzz.trimf(self.height_diff.universe, [50, 500, 500])
        
        self.aggression['defensive'] = fuzz.trimf(self.aggression.universe, [0, 0, 40])
        self.aggression['balanced'] = fuzz.trimf(self.aggression.universe, [30, 50, 70])
        self.aggression['aggressive'] = fuzz.trimf(self.aggression.universe, [60, 100, 100])
        
        self.should_jump['no'] = fuzz.trimf(self.should_jump.universe, [0, 0, 30])
        self.should_jump['maybe'] = fuzz.trimf(self.should_jump.universe, [20, 50, 80])
        self.should_jump['yes'] = fuzz.trimf(self.should_jump.universe, [70, 100, 100])
        
        # Define rules
        rule1 = ctrl.Rule(self.health['low'], self.aggression['defensive'])
        rule2 = ctrl.Rule(self.health['high'] & self.enemy_health['low'], self.aggression['aggressive'])
        rule3 = ctrl.Rule(self.distance['close'] & self.health['high'], self.aggression['aggressive'])
        rule4 = ctrl.Rule(self.distance['far'], self.aggression['balanced'])
        rule5 = ctrl.Rule(self.height_diff['below'], self.should_jump['yes'])
        rule6 = ctrl.Rule(self.height_diff['above'], self.should_jump['no'])
        rule7 = ctrl.Rule(self.health['low'] & self.distance['close'], self.should_jump['yes'])
        rule8 = ctrl.Rule(self.distance['medium'], self.should_jump['maybe'])
        
        # Create control system
        self.aggression_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
        self.jump_ctrl = ctrl.ControlSystem([rule5, rule6, rule7, rule8])
        
        self.aggression_sim = ctrl.ControlSystemSimulation(self.aggression_ctrl)
        self.jump_sim = ctrl.ControlSystemSimulation(self.jump_ctrl)
    
    def decide_action(self, ai_state, enemy_state):
        if not FUZZY_AVAILABLE:
            return SimpleFuzzyAI().decide_action(ai_state, enemy_state)
        
        # Calculate inputs
        distance = abs(ai_state['x'] - enemy_state['x'])
        height_diff = ai_state['y'] - enemy_state['y']
        
        # Compute fuzzy logic with error handling
        try:
            self.aggression_sim.input['distance'] = min(distance, 1000)
            self.aggression_sim.input['health'] = ai_state['health']
            self.aggression_sim.input['enemy_health'] = enemy_state['health']
            self.aggression_sim.compute()
            aggression = self.aggression_sim.output['aggression']
        except:
            # Fallback if fuzzy system fails
            aggression = 50.0
        
        try:
            self.jump_sim.input['height_diff'] = max(-500, min(500, height_diff))
            self.jump_sim.input['health'] = ai_state['health']
            self.jump_sim.input['distance'] = min(distance, 1000)
            self.jump_sim.compute()
            jump_desire = self.jump_sim.output['should_jump']
        except:
            # Fallback if fuzzy system fails
            jump_desire = 50.0 if height_diff > 50 else 0.0
        
        # Convert to actions
        move_towards_enemy = ai_state['x'] < enemy_state['x']
        
        return {
            'up': jump_desire > 50,
            'left': not move_towards_enemy,
            'right': move_towards_enemy,
            'down': False,
            'primaryFire': aggression > 40,
            'secondaryFire': aggression > 70
        }


def main():
    # Change to build directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(project_root, 'build')
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
                
                # Debug: print AI actions occasionally
                if frame_count % 60 == 0:  # Every second at 60 FPS
                    print(f"[DEBUG] AI Actions: {ai_actions}")
                
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
            
            print(f"\n[Frame {frame_count}] Players: {len(players)}, Bullets: {len(bullets)}")
            for player_id, p in players.items():
                player_type = "HUMAN" if player_id == list(players.keys())[0] else "AI   "
                print(f"  [{player_type}] {player_id}: HP={p['health']:5.1f}, Lives={p['lives']}, Pos=({p['x']:6.1f}, {p['y']:6.1f})")
            
            last_print = time.time()
        
        time.sleep(0.016)  # ~60 FPS
    
    print("\nGame ended!")


if __name__ == "__main__":
    main()
