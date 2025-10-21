"""
Evolvable Fuzzy AI - Uses genome parameters

This is a wrapper around the existing FuzzyAI that accepts
genome parameters for genetic algorithm evolution.

Does NOT modify the original fuzzy_ai.py file!
"""

import sys
import os

# Import the original fuzzy AI
from fuzzy.fuzzy_ai import FuzzyAI, SimpleFuzzyAI, FUZZY_AVAILABLE
from ga.fuzzy_genome import FuzzyGenome

if FUZZY_AVAILABLE:
    import numpy as np
    import skfuzzy as fuzz
    from skfuzzy import control as ctrl


class EvolvableFuzzyAI:
    """
    Fuzzy AI that uses genome parameters.
    Wraps the existing fuzzy logic but allows parameters to be evolved.
    """
    
    def __init__(self, genome: FuzzyGenome = None):
        """
        Initialize with a genome.
        
        Args:
            genome: FuzzyGenome object with evolved parameters.
                   If None, uses default parameters.
        """
        self.genome = genome if genome else FuzzyGenome()
        
        if not FUZZY_AVAILABLE:
            self.fallback_ai = SimpleFuzzyAI()
            return
        
        # Initialize fuzzy variables with genome parameters
        self._setup_fuzzy_variables()
        self._setup_membership_functions()
        self._setup_rules()
        self._create_control_systems()
        
        # Jump tracking (from original FuzzyAI)
        self.last_jump_command = False
        self.jump_frames = 0
        self.max_jump_frames = int(self.genome.genes['jump_frames'])
    
    def _setup_fuzzy_variables(self):
        """Define fuzzy variables (same as original)"""
        self.distance = ctrl.Antecedent(np.arange(0, 1301, 1), 'distance')
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
        self.enemy_health = ctrl.Antecedent(np.arange(0, 101, 1), 'enemy_health')
        self.height_diff = ctrl.Antecedent(np.arange(-400, 401, 1), 'height_diff')
        
        self.aggression = ctrl.Consequent(np.arange(0, 101, 1), 'aggression')
        self.should_jump = ctrl.Consequent(np.arange(0, 101, 1), 'should_jump')
    
    def _setup_membership_functions(self):
        """Define membership functions using GENOME PARAMETERS"""
        g = self.genome.genes  # Shorthand
        
        # Distance - evolved parameters!
        self.distance['close'] = fuzz.trimf(
            self.distance.universe, 
            [0, 0, g['distance_close_max']]
        )
        self.distance['medium'] = fuzz.trimf(
            self.distance.universe,
            [g['distance_medium_min'], 
             (g['distance_medium_min'] + g['distance_medium_max']) / 2,
             g['distance_medium_max']]
        )
        self.distance['far'] = fuzz.trimf(
            self.distance.universe,
            [g['distance_far_min'], 1000, 1300]
        )
        
        # Health - evolved parameters!
        self.health['low'] = fuzz.trimf(
            self.health.universe,
            [0, 0, g['health_low_max']]
        )
        self.health['medium'] = fuzz.trimf(
            self.health.universe,
            [g['health_medium_min'], 50, g['health_medium_max']]
        )
        self.health['high'] = fuzz.trimf(
            self.health.universe,
            [g['health_high_min'], 100, 100]
        )
        
        # Enemy health (same structure)
        self.enemy_health['low'] = fuzz.trimf(self.enemy_health.universe, [0, 0, 40])
        self.enemy_health['medium'] = fuzz.trimf(self.enemy_health.universe, [30, 50, 70])
        self.enemy_health['high'] = fuzz.trimf(self.enemy_health.universe, [60, 100, 100])
        
        # Height difference - evolved parameters!
        height_same = g['height_same_range']
        self.height_diff['below'] = fuzz.trimf(
            self.height_diff.universe,
            [-400, -400, g['height_below_max']]
        )
        self.height_diff['same'] = fuzz.trimf(
            self.height_diff.universe,
            [-height_same/2, 0, height_same/2]
        )
        self.height_diff['above'] = fuzz.trimf(
            self.height_diff.universe,
            [g['height_above_min'], 400, 400]
        )
        
        # Aggression output
        self.aggression['defensive'] = fuzz.trimf(self.aggression.universe, [0, 0, 40])
        self.aggression['balanced'] = fuzz.trimf(self.aggression.universe, [30, 50, 70])
        self.aggression['aggressive'] = fuzz.trimf(self.aggression.universe, [60, 100, 100])
        
        # Jump output
        self.should_jump['no'] = fuzz.trimf(self.should_jump.universe, [0, 0, 30])
        self.should_jump['maybe'] = fuzz.trimf(self.should_jump.universe, [20, 50, 80])
        self.should_jump['yes'] = fuzz.trimf(self.should_jump.universe, [70, 100, 100])
    
    def _setup_rules(self):
        """Define fuzzy rules (same as original)"""
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
        """Create control systems"""
        self.aggression_ctrl = ctrl.ControlSystem([self.rule1, self.rule2, self.rule3, self.rule4])
        self.jump_ctrl = ctrl.ControlSystem([self.rule5, self.rule6, self.rule7, self.rule8])
        
        self.aggression_sim = ctrl.ControlSystemSimulation(self.aggression_ctrl)
        self.jump_sim = ctrl.ControlSystemSimulation(self.jump_ctrl)
    
    def _get_platform_navigation(self, ai_state, enemy_state):
        """Platform navigation with evolved parameters"""
        ai_x, ai_y = ai_state['x'], ai_state['y']
        enemy_x, enemy_y = enemy_state['x'], enemy_state['y']
        
        g = self.genome.genes
        platform_tolerance = g['platform_y_tolerance']
        jump_zone = g['jump_zone_width']
        
        # Platform definitions
        PLATFORMS = [
            {'id': 'top', 'x1': 280, 'x2': 680, 'y': 300},
            {'id': 'bottom_left', 'x1': 100, 'x2': 400, 'y': 430},
            {'id': 'bottom_right', 'x1': 600, 'x2': 900, 'y': 430},
        ]
        
        # Detect platforms
        ai_platform = None
        enemy_platform = None
        
        for plat in PLATFORMS:
            if plat['x1'] <= ai_x <= plat['x2'] and abs(ai_y - plat['y']) < platform_tolerance:
                ai_platform = plat
            if plat['x1'] <= enemy_x <= plat['x2'] and abs(enemy_y - plat['y']) < platform_tolerance:
                enemy_platform = plat
        
        move_left = ai_x > enemy_x
        move_right = ai_x < enemy_x
        should_jump = False
        needs_double_jump = False
        
        if ai_platform and enemy_platform and ai_platform['id'] != enemy_platform['id']:
            if ai_platform['id'] in ['bottom_left', 'bottom_right'] and enemy_platform['id'] == 'top':
                needs_double_jump = True
                top_center_x = (PLATFORMS[0]['x1'] + PLATFORMS[0]['x2']) / 2
                
                if ai_x < PLATFORMS[0]['x1'] - 50:
                    move_left = False
                    move_right = True
                    if PLATFORMS[0]['x1'] - jump_zone <= ai_x <= PLATFORMS[0]['x1'] - 20:
                        should_jump = True
                elif ai_x > PLATFORMS[0]['x2'] + 50:
                    move_left = True
                    move_right = False
                    if PLATFORMS[0]['x2'] + 20 <= ai_x <= PLATFORMS[0]['x2'] + jump_zone:
                        should_jump = True
                else:
                    should_jump = True
                    move_left = ai_x > top_center_x
                    move_right = ai_x < top_center_x
            
            elif ai_platform['id'] == 'top' and enemy_platform['id'] in ['bottom_left', 'bottom_right']:
                if enemy_platform['id'] == 'bottom_left':
                    edge_x = PLATFORMS[0]['x1'] + 50
                    move_left = ai_x > edge_x
                    move_right = ai_x < edge_x
                    if ai_x <= PLATFORMS[0]['x1'] + 30:
                        should_jump = True
                        move_left = True
                else:
                    edge_x = PLATFORMS[0]['x2'] - 50
                    move_left = ai_x > edge_x
                    move_right = ai_x < edge_x
                    if ai_x >= PLATFORMS[0]['x2'] - 30:
                        should_jump = True
                        move_right = True
            
            elif ai_platform['id'] == 'bottom_left' and enemy_platform['id'] == 'bottom_right':
                needs_double_jump = True
                if ai_x < PLATFORMS[0]['x1'] - 80:
                    move_right = True
                    move_left = False
                elif PLATFORMS[0]['x1'] - jump_zone <= ai_x <= PLATFORMS[0]['x1'] - 20:
                    should_jump = True
                    move_right = True
            
            elif ai_platform['id'] == 'bottom_right' and enemy_platform['id'] == 'bottom_left':
                needs_double_jump = True
                if ai_x > PLATFORMS[0]['x2'] + 80:
                    move_left = True
                    move_right = False
                elif PLATFORMS[0]['x2'] + 20 <= ai_x <= PLATFORMS[0]['x2'] + jump_zone:
                    should_jump = True
                    move_left = True
        
        elif not ai_platform:
            move_left = ai_x > enemy_x
            move_right = ai_x < enemy_x
            should_jump = ai_y > enemy_y
        
        return move_left, move_right, should_jump, needs_double_jump
    
    def decide_action(self, ai_state, enemy_state, platforms=None):
        """Make decision using genome parameters"""
        if not FUZZY_AVAILABLE:
            return self.fallback_ai.decide_action(ai_state, enemy_state)
        
        g = self.genome.genes
        
        distance = abs(ai_state['x'] - enemy_state['x'])
        height_diff = ai_state['y'] - enemy_state['y']
        
        # Platform navigation
        nav_left, nav_right, nav_jump, needs_double_jump = self._get_platform_navigation(ai_state, enemy_state)
        
        # Fuzzy logic
        try:
            self.aggression_sim.input['distance'] = min(distance, 1300)
            self.aggression_sim.input['health'] = ai_state['health']
            self.aggression_sim.input['enemy_health'] = enemy_state['health']
            self.aggression_sim.compute()
            aggression = self.aggression_sim.output['aggression']
        except:
            aggression = 50.0
        
        try:
            self.jump_sim.input['height_diff'] = max(-400, min(400, height_diff))
            self.jump_sim.input['health'] = ai_state['health']
            self.jump_sim.input['distance'] = min(distance, 1300)
            self.jump_sim.compute()
            fuzzy_jump_desire = self.jump_sim.output['should_jump']
        except:
            fuzzy_jump_desire = 50.0
        
        # Double jump handling
        if needs_double_jump and nav_jump:
            if not self.last_jump_command:
                self.jump_frames = 0
            self.jump_frames += 1
            should_jump = self.jump_frames <= self.max_jump_frames
            self.last_jump_command = should_jump
        else:
            should_jump = nav_jump or (fuzzy_jump_desire > g['fuzzy_jump_threshold'] and abs(height_diff) < 80)
            self.last_jump_command = should_jump
            if not should_jump:
                self.jump_frames = 0
        
        # Movement
        move_left = nav_left
        move_right = nav_right

        # Spacing: avoid "shadow tracking" by keeping a preferred stand-off distance
        # Use genome parameter aggressive_distance as the target spacing on the same level
        try:
            dx = enemy_state['x'] - ai_state['x']
            dy = enemy_state['y'] - ai_state['y']
            dist = abs(dx)
            same_level = abs(dy) < 60  # roughly same platform
            target = float(g.get('aggressive_distance', 250.0))
            deadband = 40.0  # do nothing within this band to avoid oscillation

            if same_level:
                if dist < (target - deadband):
                    # Too close: back off to create space
                    move_left = dx < 0   # enemy left -> move further left
                    move_right = dx > 0  # enemy right -> move further right
                elif dist <= (target + deadband):
                    # Within comfort zone: avoid micro-tracking horizontally
                    move_left = False
                    move_right = False
                else:
                    # Farther than desired: keep approaching (nav result already does this)
                    pass
        except Exception:
            # If anything unexpected, fall back to nav behavior without spacing
            pass
        
        # Combat using evolved parameters
        can_shoot = abs(height_diff) < g['shoot_height_diff_max'] and distance < g['shoot_distance_max']
        
        return {
            'up': should_jump,
            'left': move_left,
            'right': move_right,
            'down': False,
            'primaryFire': can_shoot and aggression > g['aggression_threshold'],
            'secondaryFire': can_shoot and aggression > g['secondary_fire_threshold']
        }
