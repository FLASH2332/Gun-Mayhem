"""
Fuzzy AI Genome for Genetic Algorithm Evolution

This file defines the genome structure for evolving fuzzy logic AI parameters.
Each genome contains tunable parameters that control the fuzzy AI's behavior.
"""

import random
import json
from typing import Dict, Any


class FuzzyGenome:
    """
    Represents a genome for fuzzy logic AI parameters.
    Each parameter can be evolved through genetic algorithm.
    """
    
    def __init__(self, genome_dict: Dict[str, float] = None):
        """
        Initialize genome with parameters.
        
        Args:
            genome_dict: Optional dictionary of parameter values.
                        If None, creates random genome.
        """
        if genome_dict:
            self.genes = genome_dict.copy()
        else:
            self.genes = self._create_random_genome()
        
        # Track fitness scores
        self.fitness = 0.0
        self.wins = 0
        self.losses = 0
        self.matches_played = 0
    
    def _create_random_genome(self) -> Dict[str, float]:
        """Create random genome with all parameters within valid ranges"""
        return {
            # Distance membership function boundaries
            'distance_close_max': random.uniform(200, 500),
            'distance_medium_min': random.uniform(150, 400),
            'distance_medium_max': random.uniform(400, 800),
            'distance_far_min': random.uniform(500, 900),
            
            # Health membership function boundaries
            'health_low_max': random.uniform(20, 60),
            'health_medium_min': random.uniform(20, 50),
            'health_medium_max': random.uniform(50, 80),
            'health_high_min': random.uniform(50, 80),
            
            # Height difference boundaries
            'height_below_max': random.uniform(-80, -40),
            'height_same_range': random.uniform(50, 120),
            'height_above_min': random.uniform(40, 80),
            
            # Combat parameters
            'aggression_threshold': random.uniform(20, 70),
            'secondary_fire_threshold': random.uniform(60, 90),
            'shoot_distance_max': random.uniform(300, 700),
            'shoot_height_diff_max': random.uniform(50, 150),
            
            # Jump parameters
            'jump_frames': random.uniform(15, 30),
            'fuzzy_jump_threshold': random.uniform(40, 80),
            
            # Platform navigation parameters
            'platform_y_tolerance': random.uniform(80, 120),
            'jump_zone_width': random.uniform(60, 120),
            
            # Tactical parameters
            'retreat_health_threshold': random.uniform(10, 40),
            'aggressive_distance': random.uniform(100, 400),
        }
    
    def mutate(self, mutation_rate: float = 0.1, mutation_strength: float = 0.2):
        """
        Mutate genome parameters.
        
        Args:
            mutation_rate: Probability of each gene mutating (0.0 to 1.0)
            mutation_strength: How much to change the value (0.0 to 1.0)
        """
        for gene_name, value in self.genes.items():
            if random.random() < mutation_rate:
                # Get valid range for this gene
                min_val, max_val = self._get_gene_range(gene_name)
                
                # Calculate mutation amount
                gene_range = max_val - min_val
                mutation_amount = random.uniform(-mutation_strength, mutation_strength) * gene_range
                
                # Apply mutation and clamp to valid range
                new_value = value + mutation_amount
                self.genes[gene_name] = max(min_val, min(max_val, new_value))
    
    def _get_gene_range(self, gene_name: str) -> tuple:
        """Get valid range for a specific gene"""
        ranges = {
            'distance_close_max': (200, 500),
            'distance_medium_min': (150, 400),
            'distance_medium_max': (400, 800),
            'distance_far_min': (500, 900),
            'health_low_max': (20, 60),
            'health_medium_min': (20, 50),
            'health_medium_max': (50, 80),
            'health_high_min': (50, 80),
            'height_below_max': (-80, -40),
            'height_same_range': (50, 120),
            'height_above_min': (40, 80),
            'aggression_threshold': (20, 70),
            'secondary_fire_threshold': (60, 90),
            'shoot_distance_max': (300, 700),
            'shoot_height_diff_max': (50, 150),
            'jump_frames': (15, 30),
            'fuzzy_jump_threshold': (40, 80),
            'platform_y_tolerance': (80, 120),
            'jump_zone_width': (60, 120),
            'retreat_health_threshold': (10, 40),
            'aggressive_distance': (100, 400),
        }
        return ranges.get(gene_name, (0, 100))
    
    def crossover(self, other: 'FuzzyGenome') -> 'FuzzyGenome':
        """
        Create offspring genome by crossing over with another genome.
        Uses uniform crossover (randomly pick each gene from either parent).
        
        Args:
            other: Another FuzzyGenome to crossover with
            
        Returns:
            New FuzzyGenome offspring
        """
        child_genes = {}
        for gene_name in self.genes.keys():
            # 50/50 chance to inherit from either parent
            if random.random() < 0.5:
                child_genes[gene_name] = self.genes[gene_name]
            else:
                child_genes[gene_name] = other.genes[gene_name]
        
        return FuzzyGenome(child_genes)
    
    def save(self, filename: str):
        """Save genome to JSON file"""
        data = {
            'genes': self.genes,
            'fitness': self.fitness,
            'wins': self.wins,
            'losses': self.losses,
            'matches_played': self.matches_played
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def load(cls, filename: str) -> 'FuzzyGenome':
        """Load genome from JSON file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        genome = cls(data['genes'])
        genome.fitness = data.get('fitness', 0.0)
        genome.wins = data.get('wins', 0)
        genome.losses = data.get('losses', 0)
        genome.matches_played = data.get('matches_played', 0)
        return genome
    
    def get_summary(self) -> str:
        """Get human-readable summary of genome"""
        return f"""
Genome Summary:
  Combat Style:
    - Aggression Threshold: {self.genes['aggression_threshold']:.1f}
    - Close Range: 0-{self.genes['distance_close_max']:.0f}px
    - Shoot Distance: {self.genes['shoot_distance_max']:.0f}px
    
  Movement:
    - Jump Frames: {self.genes['jump_frames']:.0f}
    - Aggressive Distance: {self.genes['aggressive_distance']:.0f}px
    
  Performance:
    - Fitness: {self.fitness:.2f}
    - W/L: {self.wins}/{self.losses} ({self.win_rate:.1%})
    - Matches: {self.matches_played}
"""
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate"""
        if self.matches_played == 0:
            return 0.0
        return self.wins / self.matches_played
    
    def __repr__(self):
        return f"FuzzyGenome(fitness={self.fitness:.2f}, wins={self.wins}, losses={self.losses})"
