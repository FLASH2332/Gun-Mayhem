"""
Neural genome for evolving a fixed-topology neural network with GA.
Architecture (fixed):
- Inputs: 12 features
- Hidden: 16 units (tanh)
- Outputs: 6 actions (sigmoid -> threshold)

Genes: flattened list of weights and biases in order [W1, b1, W2, b2].
"""
from __future__ import annotations
import json
import math
import random
from dataclasses import dataclass, field
from typing import List, Dict

INPUT_SIZE = 12
HIDDEN_SIZE = 16
OUTPUT_SIZE = 6

# Gene layout sizes
W1_SIZE = INPUT_SIZE * HIDDEN_SIZE           # 12*16 = 192
B1_SIZE = HIDDEN_SIZE                        # 16
W2_SIZE = HIDDEN_SIZE * OUTPUT_SIZE          # 16*6 = 96
B2_SIZE = OUTPUT_SIZE                        # 6
TOTAL_GENES = W1_SIZE + B1_SIZE + W2_SIZE + B2_SIZE  # 310


def _rand_weight(scale: float = 1.0) -> float:
    # Xavier-like init range
    return random.uniform(-scale, scale)


@dataclass
class NeuralGenome:
    genes: List[float] = field(default_factory=list)
    fitness: float = 0.0
    wins: int = 0
    losses: int = 0
    matches_played: int = 0

    def __post_init__(self):
        if not self.genes:
            # Initialize with small random values
            scale1 = math.sqrt(6.0 / (INPUT_SIZE + HIDDEN_SIZE))
            scale2 = math.sqrt(6.0 / (HIDDEN_SIZE + OUTPUT_SIZE))
            # W1
            self.genes = [_rand_weight(scale1) for _ in range(W1_SIZE)]
            # b1
            self.genes += [0.0 for _ in range(B1_SIZE)]
            # W2
            self.genes += [_rand_weight(scale2) for _ in range(W2_SIZE)]
            # b2
            self.genes += [0.0 for _ in range(B2_SIZE)]

    @property
    def win_rate(self) -> float:
        return (self.wins / self.matches_played) if self.matches_played else 0.0

    def clone(self) -> "NeuralGenome":
        g = NeuralGenome(self.genes.copy())
        g.fitness = self.fitness
        g.wins = self.wins
        g.losses = self.losses
        g.matches_played = self.matches_played
        return g

    def mutate(self, mutation_rate: float = 0.15, sigma: float = 0.1):
        """Gaussian noise per gene with given probability."""
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                self.genes[i] += random.gauss(0.0, sigma)
                # clamp to avoid exploding weights
                if self.genes[i] > 3.0:
                    self.genes[i] = 3.0
                elif self.genes[i] < -3.0:
                    self.genes[i] = -3.0

    def crossover(self, other: "NeuralGenome") -> "NeuralGenome":
        child = NeuralGenome(self.genes.copy())
        for i in range(len(self.genes)):
            if random.random() < 0.5:
                child.genes[i] = other.genes[i]
        return child

    def save(self, filename: str):
        data = {
            "arch": {
                "input": INPUT_SIZE,
                "hidden": HIDDEN_SIZE,
                "output": OUTPUT_SIZE,
                "total": TOTAL_GENES,
            },
            "genes": self.genes,
            "fitness": self.fitness,
            "wins": self.wins,
            "losses": self.losses,
            "matches_played": self.matches_played,
        }
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filename: str) -> "NeuralGenome":
        with open(filename, "r") as f:
            data = json.load(f)
        genes = data["genes"]
        # Optional: validate length
        if len(genes) != TOTAL_GENES:
            raise ValueError(f"Invalid gene length {len(genes)} != {TOTAL_GENES}")
        g = NeuralGenome(genes)
        g.fitness = data.get("fitness", 0.0)
        g.wins = data.get("wins", 0)
        g.losses = data.get("losses", 0)
        g.matches_played = data.get("matches_played", 0)
        return g

    def summary(self) -> str:
        return (
            f"NeuralGenome: {len(self.genes)} genes (I={INPUT_SIZE}, H={HIDDEN_SIZE}, O={OUTPUT_SIZE})\n"
            f"  Fitness={self.fitness:.2f}, W/L={self.wins}/{self.losses} ({self.win_rate:.1%})"
        )
