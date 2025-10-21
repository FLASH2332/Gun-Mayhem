"""
Shared feature extraction logic for MARL.
Based on neural_ai.py.
"""
import math
import numpy as np
from typing import Dict, List

# These must match your neural_genome.py for consistency
INPUT_SIZE = 12

def get_observation(me: Dict, enemy: Dict) -> np.ndarray:
    """
    Builds the 12 normalized features for the RL agent.
    """
    # Positions normalized by screen (assumed 1280x720-like)
    dx = (enemy['x'] - me['x']) / 640.0  # ~ -2..2
    dy = (enemy['y'] - me['y']) / 360.0  # ~ -2..2 (positive means enemy lower)
    dist = math.hypot(dx, dy)  # ~0..3
    
    me_hp = (me['health'] / 100.0)
    en_hp = (enemy['health'] / 100.0)
    
    me_lives = (me['lives'] / 3.0)  # Assuming 3 max lives, adjust if needed
    en_lives = (enemy['lives'] / 3.0) # Assuming 3 max lives, adjust if needed
    
    # Facing: -1 left, +1 right
    facing = -1.0 if me.get('facing_direction', 1) == 0 else 1.0
    
    # Height indicators
    above = 1.0 if me['y'] < enemy['y'] - 40 else 0.0
    below = 1.0 if me['y'] > enemy['y'] + 40 else 0.0
    same_y = 1.0 if abs(me['y'] - enemy['y']) <= 40 else 0.0
    
    # Bias-like constant
    bias = 1.0
    
    features = [
        dx, dy, dist, me_hp, en_hp, me_lives, en_lives, 
        facing, above, below, same_y, bias
    ]
    
    return np.array(features, dtype=np.float32)