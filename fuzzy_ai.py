"""
Fuzzy Logic AI Controller for Gun Mayhem
Uses scikit-fuzzy to make intelligent decisions based on game state
"""

import numpy as np

# Try to import scikit-fuzzy
try:
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    print("WARNING: scikit-fuzzy not installed. Install with: pip install scikit-fuzzy")


class SimpleFuzzyAI:
    """
    Simple rule-based AI fallback if scikit-fuzzy is not available
    """
    def __init__(self):
        pass
    
    def decide_action(self, ai_state, enemy_state):
        """
        Simple rule-based decision making
        
        Args:
            ai_state: Dictionary with AI player state (health, position, etc.)
            enemy_state: Dictionary with enemy player state
            
        Returns:
            Dictionary with boolean actions (up, left, right, down, primaryFire, secondaryFire)
        """
        distance = abs(ai_state['x'] - enemy_state['x'])
        height_diff = ai_state['y'] - enemy_state['y']
        health_ratio = ai_state['health'] / 100.0
        
        # Simple rules
        should_jump = height_diff > 50  # Jump if below enemy
        move_towards_enemy = ai_state['x'] < enemy_state['x']
        should_shoot = distance < 400 and abs(height_diff) < 100
        aggressive = health_ratio > 0.5
        
        return {
            'up': should_jump,
            'left': not move_towards_enemy,
            'right': move_towards_enemy,
            'down': False,
            'primaryFire': should_shoot and aggressive,
            'secondaryFire': should_shoot and aggressive and distance < 200
        }


class FuzzyAI:
    """
    Advanced Fuzzy Logic AI Controller
    Uses scikit-fuzzy to make intelligent decisions based on:
    - Distance to enemy
    - Player health
    - Enemy health
    - Height difference
    """
    
    def __init__(self):
        if not FUZZY_AVAILABLE:
            self.fallback_ai = SimpleFuzzyAI()
            return
        
        self._setup_fuzzy_variables()
        self._setup_membership_functions()
        self._setup_rules()
        self._create_control_systems()
    
    def _setup_fuzzy_variables(self):
        """Define fuzzy input and output variables"""
        # Input variables
        self.distance = ctrl.Antecedent(np.arange(0, 1001, 1), 'distance')
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
        self.enemy_health = ctrl.Antecedent(np.arange(0, 101, 1), 'enemy_health')
        self.height_diff = ctrl.Antecedent(np.arange(-500, 501, 1), 'height_diff')
        
        # Output variables
        self.aggression = ctrl.Consequent(np.arange(0, 101, 1), 'aggression')
        self.should_jump = ctrl.Consequent(np.arange(0, 101, 1), 'should_jump')
    
    def _setup_membership_functions(self):
        """Define membership functions for fuzzy variables"""
        # Distance membership functions
        self.distance['close'] = fuzz.trimf(self.distance.universe, [0, 0, 300])
        self.distance['medium'] = fuzz.trimf(self.distance.universe, [200, 500, 800])
        self.distance['far'] = fuzz.trimf(self.distance.universe, [700, 1000, 1000])
        
        # Health membership functions
        self.health['low'] = fuzz.trimf(self.health.universe, [0, 0, 40])
        self.health['medium'] = fuzz.trimf(self.health.universe, [30, 50, 70])
        self.health['high'] = fuzz.trimf(self.health.universe, [60, 100, 100])
        
        # Enemy health membership functions
        self.enemy_health['low'] = fuzz.trimf(self.enemy_health.universe, [0, 0, 40])
        self.enemy_health['medium'] = fuzz.trimf(self.enemy_health.universe, [30, 50, 70])
        self.enemy_health['high'] = fuzz.trimf(self.enemy_health.universe, [60, 100, 100])
        
        # Height difference membership functions
        self.height_diff['below'] = fuzz.trimf(self.height_diff.universe, [-500, -500, -50])
        self.height_diff['same'] = fuzz.trimf(self.height_diff.universe, [-100, 0, 100])
        self.height_diff['above'] = fuzz.trimf(self.height_diff.universe, [50, 500, 500])
        
        # Aggression membership functions
        self.aggression['defensive'] = fuzz.trimf(self.aggression.universe, [0, 0, 40])
        self.aggression['balanced'] = fuzz.trimf(self.aggression.universe, [30, 50, 70])
        self.aggression['aggressive'] = fuzz.trimf(self.aggression.universe, [60, 100, 100])
        
        # Jump membership functions
        self.should_jump['no'] = fuzz.trimf(self.should_jump.universe, [0, 0, 30])
        self.should_jump['maybe'] = fuzz.trimf(self.should_jump.universe, [20, 50, 80])
        self.should_jump['yes'] = fuzz.trimf(self.should_jump.universe, [70, 100, 100])
    
    def _setup_rules(self):
        """Define fuzzy logic rules"""
        # Aggression rules
        self.rule1 = ctrl.Rule(self.health['low'], self.aggression['defensive'])
        self.rule2 = ctrl.Rule(self.health['high'] & self.enemy_health['low'], self.aggression['aggressive'])
        self.rule3 = ctrl.Rule(self.distance['close'] & self.health['high'], self.aggression['aggressive'])
        self.rule4 = ctrl.Rule(self.distance['far'], self.aggression['balanced'])
        
        # Jump rules
        self.rule5 = ctrl.Rule(self.height_diff['below'], self.should_jump['yes'])
        self.rule6 = ctrl.Rule(self.height_diff['above'], self.should_jump['no'])
        self.rule7 = ctrl.Rule(self.health['low'] & self.distance['close'], self.should_jump['yes'])
        self.rule8 = ctrl.Rule(self.distance['medium'], self.should_jump['maybe'])
    
    def _create_control_systems(self):
        """Create and initialize control systems"""
        self.aggression_ctrl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3, self.rule4])
        self.jump_ctrl = ctrl.ControlSystem([self.rule5, self.rule6, self.rule7, self.rule8])
        
        self.aggression_sim = ctrl.ControlSystemSimulation(self.aggression_ctrl)
        self.jump_sim = ctrl.ControlSystemSimulation(self.jump_ctrl)
    
    def decide_action(self, ai_state, enemy_state):
        """
        Make decision based on current game state using fuzzy logic
        
        Args:
            ai_state: Dictionary with AI player state
                - x, y: Position
                - health: Current health (0-100)
                - lives: Remaining lives
            enemy_state: Dictionary with enemy player state (same structure)
            
        Returns:
            Dictionary with boolean actions:
                - up: Jump
                - left: Move left
                - right: Move right
                - down: Move down
                - primaryFire: Shoot primary weapon
                - secondaryFire: Shoot secondary weapon
        """
        if not FUZZY_AVAILABLE:
            return self.fallback_ai.decide_action(ai_state, enemy_state)
        
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
        
        # Convert fuzzy outputs to game actions
        move_towards_enemy = ai_state['x'] < enemy_state['x']
        
        return {
            'up': jump_desire > 50,
            'left': not move_towards_enemy,
            'right': move_towards_enemy,
            'down': False,
            'primaryFire': aggression > 40,
            'secondaryFire': aggression > 70
        }
    
    def get_fuzzy_state(self, ai_state, enemy_state):
        """
        Get the fuzzy logic state for debugging/visualization
        
        Returns:
            Dictionary with aggression and jump_desire values
        """
        if not FUZZY_AVAILABLE:
            return {'aggression': 50.0, 'jump_desire': 50.0}
        
        distance = abs(ai_state['x'] - enemy_state['x'])
        height_diff = ai_state['y'] - enemy_state['y']
        
        try:
            self.aggression_sim.input['distance'] = min(distance, 1000)
            self.aggression_sim.input['health'] = ai_state['health']
            self.aggression_sim.input['enemy_health'] = enemy_state['health']
            self.aggression_sim.compute()
            aggression = self.aggression_sim.output['aggression']
        except:
            aggression = 50.0
        
        try:
            self.jump_sim.input['height_diff'] = max(-500, min(500, height_diff))
            self.jump_sim.input['health'] = ai_state['health']
            self.jump_sim.input['distance'] = min(distance, 1000)
            self.jump_sim.compute()
            jump_desire = self.jump_sim.output['should_jump']
        except:
            jump_desire = 50.0
        
        return {
            'aggression': aggression,
            'jump_desire': jump_desire,
            'distance': distance,
            'height_diff': height_diff
        }
