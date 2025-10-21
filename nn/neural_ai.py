"""
Neural AI controller using a fixed-topology feed-forward network evolved via GA.
- Inputs (12): normalized features from player and enemy states
- Hidden: 16 tanh
- Outputs (6): action probabilities (sigmoid) -> threshold to booleans
"""
from __future__ import annotations
import math
from typing import Dict, List
from ga.neural_genome import (
    NeuralGenome, INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE,
    W1_SIZE, B1_SIZE, W2_SIZE, B2_SIZE
)


def tanh(x: float) -> float:
    return math.tanh(x)


def sigmoid(x: float) -> float:
    # clamp to avoid overflow
    if x < -50:
        return 0.0
    if x > 50:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


class NeuralAI:
    def __init__(self, genome: NeuralGenome, action_threshold: float = 0.5):
        self.genome = genome
        self.action_threshold = action_threshold
        # unpack weights/biases views (no copies)
        g = genome.genes
        self.W1 = g[0:W1_SIZE]
        self.b1 = g[W1_SIZE:W1_SIZE+B1_SIZE]
        off = W1_SIZE + B1_SIZE
        self.W2 = g[off:off+W2_SIZE]
        self.b2 = g[off+W2_SIZE:off+W2_SIZE+B2_SIZE]
        # jump hold state
        self.jump_hold_frames = 0
        self.max_jump_hold = 20  # consistent with double-jump requirement

    def _dot_mv(self, W: List[float], x: List[float], out_dim: int, in_dim: int, b: List[float]) -> List[float]:
        # y = W x + b; W is row-major [out_dim x in_dim]
        y = [0.0] * out_dim
        idx = 0
        for o in range(out_dim):
            s = 0.0
            base = o * in_dim
            for i in range(in_dim):
                s += W[base + i] * x[i]
            y[o] = s + b[o]
        return y

    def _forward(self, x: List[float]) -> List[float]:
        # Layer1
        h = self._dot_mv(self.W1, x, HIDDEN_SIZE, INPUT_SIZE, self.b1)
        h = [tanh(v) for v in h]
        # Layer2
        o = self._dot_mv(self.W2, h, OUTPUT_SIZE, HIDDEN_SIZE, self.b2)
        o = [sigmoid(v) for v in o]
        return o

    def _features(self, me: Dict, enemy: Dict) -> List[float]:
        # Build 12 normalized features
        # Positions normalized by screen (assumed 1280x720-like)
        dx = (enemy['x'] - me['x']) / 640.0  # ~ -2..2
        dy = (enemy['y'] - me['y']) / 360.0  # ~ -2..2 (positive means enemy lower)
        dist = math.hypot(dx, dy)  # ~0..3
        me_hp = (me['health'] / 100.0)
        en_hp = (enemy['health'] / 100.0)
        me_lives = (me['lives'] / 3.0)
        en_lives = (enemy['lives'] / 3.0)
        # Facing: -1 left, +1 right
        facing = -1.0 if me.get('facing_direction', 1) == 0 else 1.0
        # Height indicators
        above = 1.0 if me['y'] < enemy['y'] - 40 else 0.0
        below = 1.0 if me['y'] > enemy['y'] + 40 else 0.0
        same_y = 1.0 if abs(me['y'] - enemy['y']) <= 40 else 0.0
        # Bias-like constant
        bias = 1.0
        return [dx, dy, dist, me_hp, en_hp, me_lives, en_lives, facing, above, below, same_y, bias]

    def decide_action(self, me: Dict, enemy: Dict) -> Dict[str, bool]:
        x = self._features(me, enemy)
        probs = self._forward(x)
        up_p, left_p, down_p, right_p, primary_p, secondary_p = probs

        # Jump hold logic for double-jump/platform reach
        up = up_p > self.action_threshold
        if up:
            self.jump_hold_frames = min(self.max_jump_hold, self.jump_hold_frames + 1)
        else:
            self.jump_hold_frames = max(0, self.jump_hold_frames - 2)
        up_pressed = self.jump_hold_frames > 0

        actions = {
            'up': up_pressed,
            'left': left_p > self.action_threshold,
            'down': down_p > self.action_threshold,
            'right': right_p > self.action_threshold,
            'primaryFire': primary_p > self.action_threshold,
            'secondaryFire': secondary_p > self.action_threshold,
        }
        return actions
