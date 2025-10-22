"""
Genome for GA Sequence Optimization.
The genome is a fixed-length list of action "chunks".
Each chunk has 3 integer values:
- horizontal: 0=Left, 1=Right, 2=None
- vertical: 0=Up, 1=Down, 2=None
- shoot: 0=Primary, 1=Secondary, 2=None
"""
import random
import json
from typing import List, Dict

# --- Genome Configuration ---
RECORD_DURATION_SEC = 10
FPS = 60
FRAMES_PER_WINDOW = 10  # This is your "window"
# ---

TOTAL_FRAMES = RECORD_DURATION_SEC * FPS
NUM_WINDOWS = TOTAL_FRAMES // FRAMES_PER_WINDOW # Should be 60

class SequenceGenome:
    def __init__(self, genes: List[Dict[str, int]] = None):
        if genes:
            self.genes = genes
        else:
            self.genes = self._create_random_genome()
            
        self.fitness = 0.0

    def _create_random_genome(self) -> List[Dict[str, int]]:
        """Creates a list of 60 random action chunks."""
        genome = []
        for _ in range(NUM_WINDOWS):
            chunk = {
                'horizontal': random.randint(0, 2),
                'vertical': random.randint(0, 2),
                'shoot': random.randint(0, 2)
            }
            genome.append(chunk)
        return genome

    def get_action_for_frame(self, frame: int) -> Dict[str, int]:
        """Gets the action chunk (as ints) for the current frame."""
        window_index = frame // FRAMES_PER_WINDOW
        if window_index >= len(self.genes):
            # If game runs long, just hold the last action
            window_index = len(self.genes) - 1
            
        return self.genes[window_index]

    def crossover(self, other: 'SequenceGenome') -> 'SequenceGenome':
        """Performs single-point crossover."""
        crossover_point = random.randint(1, NUM_WINDOWS - 2)
        
        child_genes = (
            self.genes[:crossover_point] + 
            other.genes[crossover_point:]
        )
        return SequenceGenome(child_genes)

    def mutate(self, mutation_rate: float = 0.1):
        """
        Mutates the genome.
        mutation_rate is the chance *per window* to change.
        """
        for i in range(len(self.genes)):
            if random.random() < mutation_rate:
                # Pick one gene key to mutate
                key_to_mutate = random.choice(['horizontal', 'vertical', 'shoot'])
                
                # Pick a new value, ensuring it's different
                current_val = self.genes[i][key_to_mutate]
                new_val = random.randint(0, 2)
                while new_val == current_val:
                    new_val = random.randint(0, 2)
                
                self.genes[i][key_to_mutate] = new_val
    
    def save(self, filename: str):
        with open(filename, 'w') as f:
            data = {'genes': self.genes, 'fitness': self.fitness}
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filename: str) -> 'SequenceGenome':
        with open(filename, 'r') as f:
            data = json.load(f)
        g = cls(data['genes'])
        g.fitness = data.get('fitness', 0.0)
        return g