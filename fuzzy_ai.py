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
    Includes basic platform navigation logic with double jump support
    """
    def __init__(self):
        self.jump_frames = 0
        self.max_jump_frames = 20  # Keep jumping for ~0.33 seconds
        self.last_jump_command = False
    
    def _check_platform_level(self, y_pos):
        """Determine which platform level the position is on"""
        if abs(y_pos - 300) < 100:
            return 'top'
        elif abs(y_pos - 430) < 100:
            return 'bottom'
        return 'airborne'
    
    def decide_action(self, ai_state, enemy_state):
        """
        Simple rule-based decision making with basic platform navigation
        Platform height (130px) requires DOUBLE JUMP (single jump = 128px)
        
        Args:
            ai_state: Dictionary with AI player state (health, position, etc.)
            enemy_state: Dictionary with enemy player state
            
        Returns:
            Dictionary with boolean actions (up, left, right, down, primaryFire, secondaryFire)
        """
        ai_x, ai_y = ai_state['x'], ai_state['y']
        enemy_x, enemy_y = enemy_state['x'], enemy_state['y']
        
        distance = abs(ai_x - enemy_x)
        height_diff = ai_y - enemy_y
        health_ratio = ai_state['health'] / 100.0
        
        # Determine platform levels
        ai_level = self._check_platform_level(ai_y)
        enemy_level = self._check_platform_level(enemy_y)
        
        # Default movement: towards enemy
        move_left = ai_x > enemy_x
        move_right = ai_x < enemy_x
        should_jump = False
        needs_double_jump = False
        
        # Platform-aware navigation
        if ai_level == 'bottom' and enemy_level == 'top':
            needs_double_jump = True  # 130px height needs double jump!
            # Need to jump up - move towards center gap
            if ai_x < 260:  # Too far left
                move_right = True
                move_left = False
            elif ai_x > 700:  # Too far right
                move_left = True
                move_right = False
            # Jump when in position (keep jumping to trigger double jump)
            if 260 <= ai_x <= 700:
                should_jump = True
                
        elif ai_level == 'top' and enemy_level == 'bottom':
            # Need to drop down - move to edge
            if enemy_x < 480:  # Enemy on left side
                move_left = ai_x > 300
                move_right = ai_x < 300
            else:  # Enemy on right side
                move_left = ai_x > 650
                move_right = ai_x < 650
        
        else:
            # Same level or airborne - basic navigation
            should_jump = height_diff > 50
            move_left = ai_x > enemy_x
            move_right = ai_x < enemy_x
        
        # Handle double jump - keep jump button pressed for multiple frames
        if needs_double_jump and should_jump:
            if not self.last_jump_command:
                self.jump_frames = 0  # Start new jump sequence
            self.jump_frames += 1
            should_jump = self.jump_frames <= self.max_jump_frames
            self.last_jump_command = should_jump
        else:
            self.last_jump_command = should_jump
            if not should_jump:
                self.jump_frames = 0
        
        # Combat decisions
        should_shoot = distance < 400 and abs(height_diff) < 100
        aggressive = health_ratio > 0.5
        
        return {
            'up': should_jump,
            'left': move_left,
            'right': move_right,
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
        
        # Track jumping state for double jumps
        self.last_jump_command = False
        self.jump_frames = 0  # Frames since jump started
        self.max_jump_frames = 20  # Keep jumping for ~0.33 seconds to ensure double jump
    
    def _setup_fuzzy_variables(self):
        """
        Define fuzzy input and output variables
        
        Parameter reasoning based on game mechanics:
        - distance: 0-1300 (screen width = 1280px)
        - health: 0-100 (matches maxHealth in Player.hpp)
        - enemy_health: 0-100 (same as above)
        - height_diff: -400 to 400 (max jump height ~256px, platform spacing ~130px)
        
        Game mechanics reference:
        - Player speed: 300 units/sec
        - Bullet speed: 1000 units/sec
        - Jump speed: 800 units/sec with gravity 2500
        - Max jump height: ~128px per jump, 256px with double jump
        """
        # Input variables
        self.distance = ctrl.Antecedent(np.arange(0, 1301, 1), 'distance')  # Covers full screen width
        self.health = ctrl.Antecedent(np.arange(0, 101, 1), 'health')
        self.enemy_health = ctrl.Antecedent(np.arange(0, 101, 1), 'enemy_health')
        self.height_diff = ctrl.Antecedent(np.arange(-400, 401, 1), 'height_diff')  # Realistic vertical range
        
        # Output variables
        self.aggression = ctrl.Consequent(np.arange(0, 101, 1), 'aggression')
        self.should_jump = ctrl.Consequent(np.arange(0, 101, 1), 'should_jump')
    
    def _setup_membership_functions(self):
        """
        Define membership functions for fuzzy variables
        
        Distance thresholds based on combat mechanics:
        - close (0-350): Optimal shooting range (bullet travel time ~0.35s)
        - medium (250-700): Mid-range combat zone
        - far (600-1300): Long-range, harder to hit moving targets
        
        Height thresholds based on jump mechanics:
        - below (-400 to -60): Need to jump to reach enemy (jump height ~128-256px)
        - same (-80 to 80): Same platform level (±player height ~64px)
        - above (60 to 400): Enemy is lower, no jump needed
        """
        # Distance membership functions (optimized for 1000 units/sec bullet speed)
        self.distance['close'] = fuzz.trimf(self.distance.universe, [0, 0, 350])      # Point-blank to effective range
        self.distance['medium'] = fuzz.trimf(self.distance.universe, [250, 500, 700])  # Mid-range combat
        self.distance['far'] = fuzz.trimf(self.distance.universe, [600, 1000, 1300])   # Long-range
        
        # Health membership functions (standard thresholds)
        self.health['low'] = fuzz.trimf(self.health.universe, [0, 0, 40])
        self.health['medium'] = fuzz.trimf(self.health.universe, [30, 50, 70])
        self.health['high'] = fuzz.trimf(self.health.universe, [60, 100, 100])
        
        # Enemy health membership functions
        self.enemy_health['low'] = fuzz.trimf(self.enemy_health.universe, [0, 0, 40])
        self.enemy_health['medium'] = fuzz.trimf(self.enemy_health.universe, [30, 50, 70])
        self.enemy_health['high'] = fuzz.trimf(self.enemy_health.universe, [60, 100, 100])
        
        # Height difference (based on jump height ~128px and platform spacing)
        self.height_diff['below'] = fuzz.trimf(self.height_diff.universe, [-400, -400, -60])  # Enemy significantly higher
        self.height_diff['same'] = fuzz.trimf(self.height_diff.universe, [-80, 0, 80])        # Same level (±player height)
        self.height_diff['above'] = fuzz.trimf(self.height_diff.universe, [60, 400, 400])     # Enemy lower
        
        # Aggression membership functions (tactical behavior)
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
    
    def _get_platform_navigation(self, ai_state, enemy_state, platforms=None):
        """
        Platform-aware navigation logic
        
        Handles multi-level navigation by detecting:
        1. If AI and enemy are on different vertical levels
        2. Where AI needs to move to reach the enemy's level
        3. When to jump to change levels
        
        Platform layout (hardcoded for now):
        - Top level: Platform1 at x=280-680, y=300
        - Bottom level: Platform2 at x=100-400, y=430 (left)
        - Bottom level: Platform3 at x=600-900, y=430 (right)
        """
        ai_x, ai_y = ai_state['x'], ai_state['y']
        enemy_x, enemy_y = enemy_state['x'], enemy_state['y']
        
        # Platform definitions (from gameConfig.json)
        PLATFORMS = [
            {'id': 'top', 'x1': 280, 'x2': 680, 'y': 300},      # Top middle platform
            {'id': 'bottom_left', 'x1': 100, 'x2': 400, 'y': 430},   # Bottom left
            {'id': 'bottom_right', 'x1': 600, 'x2': 900, 'y': 430},  # Bottom right
        ]
        
        # Determine which platform AI is on/near
        ai_platform = None
        enemy_platform = None
        
        for plat in PLATFORMS:
            # Check if AI is on this platform (within x range, near y level)
            if plat['x1'] <= ai_x <= plat['x2'] and abs(ai_y - plat['y']) < 100:
                ai_platform = plat
            # Check if enemy is on this platform
            if plat['x1'] <= enemy_x <= plat['x2'] and abs(enemy_y - plat['y']) < 100:
                enemy_platform = plat
        
        # Default navigation: move towards enemy
        move_left = ai_x > enemy_x
        move_right = ai_x < enemy_x
        should_jump = False
        needs_double_jump = False  # Flag for situations requiring double jump
        
        # If on different platforms, navigate intelligently
        if ai_platform and enemy_platform and ai_platform['id'] != enemy_platform['id']:
            
            # CASE 1: AI on bottom, enemy on top (REQUIRES DOUBLE JUMP - 130px height > 128px single jump)
            if ai_platform['id'] in ['bottom_left', 'bottom_right'] and enemy_platform['id'] == 'top':
                needs_double_jump = True  # 130px height requires double jump!
                
                # Move towards the center gap to jump up
                top_center_x = (PLATFORMS[0]['x1'] + PLATFORMS[0]['x2']) / 2  # x=480
                
                # Navigate towards position under the top platform
                if ai_x < PLATFORMS[0]['x1'] - 50:  # Too far left
                    move_left = False
                    move_right = True
                    # Start jumping when getting close
                    if PLATFORMS[0]['x1'] - 100 <= ai_x <= PLATFORMS[0]['x1'] - 20:
                        should_jump = True
                        
                elif ai_x > PLATFORMS[0]['x2'] + 50:  # Too far right
                    move_left = True
                    move_right = False
                    # Start jumping when getting close
                    if PLATFORMS[0]['x2'] + 20 <= ai_x <= PLATFORMS[0]['x2'] + 100:
                        should_jump = True
                        
                else:  # In range of top platform - DOUBLE JUMP to reach it
                    should_jump = True
                    # Fine-tune horizontal movement while jumping
                    move_left = ai_x > top_center_x
                    move_right = ai_x < top_center_x
            
            # CASE 2: AI on top, enemy on bottom
            elif ai_platform['id'] == 'top' and enemy_platform['id'] in ['bottom_left', 'bottom_right']:
                # Determine which bottom platform enemy is on
                if enemy_platform['id'] == 'bottom_left':
                    # Move towards left edge of top platform
                    edge_x = PLATFORMS[0]['x1'] + 50  # x=330
                    move_left = ai_x > edge_x
                    move_right = ai_x < edge_x
                    
                    # Jump off when near left edge
                    if ai_x <= PLATFORMS[0]['x1'] + 30:
                        should_jump = True  # Will fall to bottom left
                        move_left = True
                        
                else:  # enemy on bottom_right
                    # Move towards right edge of top platform
                    edge_x = PLATFORMS[0]['x2'] - 50  # x=630
                    move_left = ai_x > edge_x
                    move_right = ai_x < edge_x
                    
                    # Jump off when near right edge
                    if ai_x >= PLATFORMS[0]['x2'] - 30:
                        should_jump = True  # Will fall to bottom right
                        move_right = True
            
            # CASE 3: AI on one bottom platform, enemy on the other
            elif ai_platform['id'] == 'bottom_left' and enemy_platform['id'] == 'bottom_right':
                needs_double_jump = True  # Need double jump to reach top platform
                # Need to go through top platform
                # First, get to position where we can jump up
                if ai_x < PLATFORMS[0]['x1'] - 80:
                    move_right = True
                    move_left = False
                elif PLATFORMS[0]['x1'] - 100 <= ai_x <= PLATFORMS[0]['x1'] - 20:
                    should_jump = True
                    move_right = True
                    
            elif ai_platform['id'] == 'bottom_right' and enemy_platform['id'] == 'bottom_left':
                needs_double_jump = True  # Need double jump to reach top platform
                # Need to go through top platform
                if ai_x > PLATFORMS[0]['x2'] + 80:
                    move_left = True
                    move_right = False
                elif PLATFORMS[0]['x2'] + 20 <= ai_x <= PLATFORMS[0]['x2'] + 100:
                    should_jump = True
                    move_left = True
        
        # If not on a platform (falling/jumping), use basic navigation
        elif not ai_platform:
            move_left = ai_x > enemy_x
            move_right = ai_x < enemy_x
            should_jump = ai_y > enemy_y  # Jump if below enemy
        
        return move_left, move_right, should_jump, needs_double_jump
    
    def decide_action(self, ai_state, enemy_state, platforms=None):
        """
        Make decision based on current game state using fuzzy logic + platform navigation
        
        Args:
            ai_state: Dictionary with AI player state
                - x, y: Position
                - health: Current health (0-100)
                - lives: Remaining lives
            enemy_state: Dictionary with enemy player state (same structure)
            platforms: Optional platform data (not used yet, hardcoded for now)
            
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
        
        # Get platform-aware navigation (now returns 4 values including double jump flag)
        nav_left, nav_right, nav_jump, needs_double_jump = self._get_platform_navigation(ai_state, enemy_state, platforms)
        
        # Compute fuzzy logic for combat decisions
        try:
            self.aggression_sim.input['distance'] = min(distance, 1300)
            self.aggression_sim.input['health'] = ai_state['health']
            self.aggression_sim.input['enemy_health'] = enemy_state['health']
            self.aggression_sim.compute()
            aggression = self.aggression_sim.output['aggression']
        except:
            aggression = 50.0
        
        # Compute fuzzy logic for jump desire (for fine-tuning)
        try:
            self.jump_sim.input['height_diff'] = max(-400, min(400, height_diff))
            self.jump_sim.input['health'] = ai_state['health']
            self.jump_sim.input['distance'] = min(distance, 1300)
            self.jump_sim.compute()
            fuzzy_jump_desire = self.jump_sim.output['should_jump']
        except:
            fuzzy_jump_desire = 50.0
        
        # Handle double jump logic for reaching platforms
        if needs_double_jump and nav_jump:
            # Start or continue jump sequence
            if not self.last_jump_command:
                # Starting new jump
                self.jump_frames = 0
            self.jump_frames += 1
            
            # Keep jump pressed for multiple frames to ensure double jump triggers
            should_jump = self.jump_frames <= self.max_jump_frames
            self.last_jump_command = should_jump
        else:
            # Normal jump logic
            should_jump = nav_jump or (fuzzy_jump_desire > 60 and abs(height_diff) < 80)
            self.last_jump_command = should_jump
            if not should_jump:
                self.jump_frames = 0  # Reset counter when not jumping
        
        # Use platform navigation for movement
        move_left = nav_left
        move_right = nav_right
        
        # Shoot when on same level or close enough
        can_shoot = abs(height_diff) < 100 and distance < 500
        
        return {
            'up': should_jump,
            'left': move_left,
            'right': move_right,
            'down': False,
            'primaryFire': can_shoot and aggression > 40,
            'secondaryFire': can_shoot and aggression > 70
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
