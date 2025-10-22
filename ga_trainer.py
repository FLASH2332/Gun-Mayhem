"""
Genetic Algorithm Trainer for Fuzzy AI

Evolves population of 100 bots that fight each other.
Fitness = survival (wins when enemy reaches 0 lives).

Does NOT modify existing code - completely separate training system!
"""

import os
import sys
import time
import random
import json
import math
from typing import List, Tuple
import multiprocessing as mp

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
from ga.fuzzy_genome import FuzzyGenome
from fuzzy.evolvable_fuzzy_ai import EvolvableFuzzyAI


class GeneticTrainer:
    """
    Genetic Algorithm trainer for evolving fuzzy AI bots.
    """
    
    def __init__(self, population_size=5, elite_size=2):
        """
        Initialize GA trainer.
        
        Args:
            population_size: Number of bots in population (default: 100)
            elite_size: Number of top bots to keep each generation (default: 10)
        """
        self.population_size = population_size
        self.elite_size = elite_size
        self.population: List[FuzzyGenome] = []
        self.generation = 0
        self.best_genome = None
        self.best_fitness = 0.0
        
        # Evolution parameters
        self.mutation_rate = 0.15  # 15% chance per gene
        self.mutation_strength = 0.2  # 20% of gene range
        self.tournament_size = 5  # Each bot fights 5 opponents per evaluation
        
        # Create evolved_genomes folder for saving
        self.genomes_dir = "evolved_genomes"
        if not os.path.exists(self.genomes_dir):
            os.makedirs(self.genomes_dir)
            print(f"Created '{self.genomes_dir}/' directory for saving genomes\n")
        
        print("=" * 70)
        print("GENETIC ALGORITHM TRAINER FOR FUZZY AI")
        print("=" * 70)
        print(f"Population Size: {population_size}")
        print(f"Elite Size: {elite_size}")
        print(f"Tournament Size: {self.tournament_size}")
        print(f"Training Mode: HEADLESS (no rendering, faster training)")
        print()
        print("NOTE: SDL2 windows will be created and destroyed for each match.")
        print("      Each window is cleaned up immediately after the match.")
        print("      You may see brief flashes - this is normal during training.")
        print("=" * 70)
    
    def initialize_population(self):
        """Create initial random population"""
        print(f"\n[INIT] Creating {self.population_size} random genomes...")
        self.population = [FuzzyGenome() for _ in range(self.population_size)]
        print(f"[INIT] Population initialized!")
    
    def play_match(self, genome1: FuzzyGenome, genome2: FuzzyGenome, 
                   max_frames=3600, headless=True) -> Tuple[str, dict]:
        """
        Play a match between two genomes.
        
        Args:
            genome1: First bot's genome
            genome2: Second bot's genome
            max_frames: Maximum frames before declaring draw (default: 3600 = 60 seconds)
            headless: Run without rendering (faster, default: True)
            
        Returns:
            Tuple of (winner_id, match_stats)
            winner_id: 'player1', 'player2', or 'draw'
            
        Note:
            Even in headless mode, SDL2 creates a window (but doesn't render to it).
            This is unavoidable without modifying the C++ game engine.
            The window will be mostly invisible and performance is still good.
        """
        # Change to build directory
        project_root = os.path.dirname(os.path.abspath(__file__))
        build_dir = os.path.join(project_root, 'build')
        if not os.path.exists(build_dir):
            os.makedirs(build_dir)
        original_dir = os.getcwd()
        os.chdir(build_dir)
        
        try:
            # Initialize game (creates SDL window even in headless mode)
            game = gunmayhem.GameRunner()
            if not game.init_game("GA Training - Bot vs Bot"):
                print("[ERROR] Failed to initialize game!")
                os.chdir(original_dir)
                return 'draw', {}
            
            # Create AIs
            ai1 = EvolvableFuzzyAI(genome1)
            ai2 = EvolvableFuzzyAI(genome2)
            
            # Create wrappers
            game_state = gunmayhem.GameState()
            game_control = gunmayhem.GameControl()
            
            frame_count = 0
            players_disabled = False
            # engagement stats
            total_distance = 0.0
            distance_samples = 0
            shots1 = 0
            shots2 = 0
            
            # Game loop
            while game.is_running() and frame_count < max_frames:
                game.handle_events()
                
                players = game_state.get_all_players()
                
                if len(players) >= 2:
                    player_ids = list(players.keys())
                    
                    # Disable keyboard once
                    if not players_disabled:
                        game_control.disable_keyboard_for_player(player_ids[0])
                        game_control.disable_keyboard_for_player(player_ids[1])
                        players_disabled = True
                    
                    player1_state = players[player_ids[0]]
                    player2_state = players[player_ids[1]]

                    # accumulate distance
                    dx = player2_state['x'] - player1_state['x']
                    dy = player2_state['y'] - player1_state['y']
                    total_distance += math.hypot(dx, dy)
                    distance_samples += 1
                    
                    # Check win condition: opponent has 0 lives
                    if player2_state['lives'] <= 0:
                        game.quit()  # Clean up SDL window
                        os.chdir(original_dir)
                        return 'player1', {
                            'frames': frame_count,
                            'winner_health': player1_state['health'],
                            'winner_lives': player1_state['lives']
                        }
                    
                    if player1_state['lives'] <= 0:
                        game.quit()  # Clean up SDL window
                        os.chdir(original_dir)
                        return 'player2', {
                            'frames': frame_count,
                            'winner_health': player2_state['health'],
                            'winner_lives': player2_state['lives']
                        }
                    
                    # AI decisions
                    ai1_actions = ai1.decide_action(player1_state, player2_state)
                    ai2_actions = ai2.decide_action(player2_state, player1_state)
                    # track shooting attempts
                    if ai1_actions.get('primaryFire'): shots1 += 1
                    if ai2_actions.get('primaryFire'): shots2 += 1
                    
                    # Send controls
                    game_control.set_player_movement(
                        player_ids[0],
                        bool(ai1_actions['up']),
                        bool(ai1_actions['left']),
                        bool(ai1_actions['down']),
                        bool(ai1_actions['right']),
                        bool(ai1_actions['primaryFire']),
                        bool(ai1_actions['secondaryFire'])
                    )
                    
                    game_control.set_player_movement(
                        player_ids[1],
                        bool(ai2_actions['up']),
                        bool(ai2_actions['left']),
                        bool(ai2_actions['down']),
                        bool(ai2_actions['right']),
                        bool(ai2_actions['primaryFire']),
                        bool(ai2_actions['secondaryFire'])
                    )
                
                # Update game physics
                game.update(0.0166)
                
                # Only render if not headless (skip rendering for fast training)
                if not headless:
                    game.render()
                
                frame_count += 1
            
            # If we get here, it's a draw (timeout)
            game.quit()  # Clean up SDL window
            os.chdir(original_dir)
            avg_dist = (total_distance / distance_samples) if distance_samples else 9999.0
            return 'draw', {
                'frames': frame_count,
                'avg_distance': avg_dist,
                'shots1': shots1,
                'shots2': shots2,
                'p1_health': player1_state['health'] if distance_samples else 0.0,
                'p2_health': player2_state['health'] if distance_samples else 0.0,
            }
        
        except Exception as e:
            print(f"[ERROR] Match failed: {e}")
            try:
                game.quit()  # Try to clean up even on error
            except:
                pass
            os.chdir(original_dir)
            return 'draw', {}
    
    def evaluate_fitness(self, genome: FuzzyGenome, opponent_pool: List[FuzzyGenome]) -> float:
        """
        Evaluate fitness by fighting against random opponents.
        
        Args:
            genome: Genome to evaluate
            opponent_pool: Pool of opponents to fight against
            
        Returns:
            Fitness score (higher is better)
        """
        wins = 0
        losses = 0
        total_score = 0.0
        
        # Select random opponents
        opponents = random.sample(opponent_pool, min(self.tournament_size, len(opponent_pool)))
        
        for opponent in opponents:
            # Shorter matches to reduce stalemates and speed up learning
            winner, stats = self.play_match(genome, opponent, max_frames=1200, headless=True)
            
            if winner == 'player1':
                wins += 1
                # Bonus points for faster wins and remaining health
                speed_bonus = max(0, 1200 - stats.get('frames', 1200)) / 100
                health_bonus = stats.get('winner_health', 0) / 10
                lives_bonus = stats.get('winner_lives', 0) * 50
                total_score += 100 + speed_bonus + health_bonus + lives_bonus
            
            elif winner == 'player2':
                losses += 1
                total_score += 0  # Loss = 0 points
            
            else:
                # Timeout: decide a technical winner by remaining health
                p1_hp = stats.get('p1_health', 0.0)
                p2_hp = stats.get('p2_health', 0.0)
                avg_dist = stats.get('avg_distance', 2000.0)
                shots1 = stats.get('shots1', 0)
                # engagement features reused
                proximity_bonus = max(0.0, 500.0 - min(500.0, avg_dist)) / 10.0  # 0..50
                shots_bonus = min(20.0, shots1 * 0.5)

                if p1_hp > p2_hp + 0.5:
                    # Count as technical WIN for player1
                    wins += 1
                    speed_bonus = 0.0  # no KO, keep modest
                    health_bonus = (p1_hp - p2_hp) / 2.0  # reward clear advantage
                    lives_bonus = 0
                    total_score += 60 + speed_bonus + health_bonus + proximity_bonus + shots_bonus
                elif p2_hp > p1_hp + 0.5:
                    # Count as technical LOSS for player1
                    losses += 1
                    # small shaping still applied to avoid zero-signal
                    total_score += max(0.0, proximity_bonus + shots_bonus - 5.0)
                else:
                    # True draw — equal health: small shaped reward to break ties
                    base_draw = 5.0
                    hp_bonus = 0.0
                    total_score += base_draw + proximity_bonus + shots_bonus + hp_bonus
        
        # Update genome stats
        genome.wins = wins
        genome.losses = losses
        genome.matches_played = len(opponents)
        genome.fitness = total_score / len(opponents)  # Average fitness
        
        return genome.fitness
    
    def selection(self) -> List[FuzzyGenome]:
        """
        Select elite genomes for next generation.
        
        Returns:
            List of elite genomes
        """
        # Sort by fitness (descending)
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        
        # Return top performers
        return sorted_pop[:self.elite_size]
    
    def crossover_and_mutate(self, elites: List[FuzzyGenome]) -> List[FuzzyGenome]:
        """
        Create offspring through crossover and mutation.
        
        Args:
            elites: Elite genomes to breed from
            
        Returns:
            New population including elites and offspring
        """
        new_population = elites.copy()  # Keep elites
        
        # Create offspring to fill rest of population
        while len(new_population) < self.population_size:
            # Select two random parents from elites
            parent1, parent2 = random.sample(elites, 2)
            
            # Crossover
            child = parent1.crossover(parent2)
            
            # Mutate
            child.mutate(self.mutation_rate, self.mutation_strength)
            
            new_population.append(child)
        
        return new_population
    
    def evolve_generation(self):
        """Run one generation of evolution"""
        print(f"\n{'='*70}")
        print(f"GENERATION {self.generation}")
        print(f"{'='*70}")
        
        # Evaluate fitness for each genome
        print(f"\n[EVAL] Evaluating {len(self.population)} genomes...")
        print(f"       Each fights {self.tournament_size} opponents...")
        
        start_time = time.time()
        
        for i, genome in enumerate(self.population):
            # Use rest of population as opponent pool
            opponent_pool = [g for g in self.population if g is not genome]
            
            fitness = self.evaluate_fitness(genome, opponent_pool)
            
            if (i + 1) % 10 == 0 or (i + 1) == len(self.population):
                elapsed = time.time() - start_time
                eta = (elapsed / (i + 1)) * (len(self.population) - (i + 1))
                print(f"       [{i+1}/{len(self.population)}] "
                      f"Fitness: {fitness:.2f} | "
                      f"ETA: {eta:.1f}s")
        
        # Find best genome
        best = max(self.population, key=lambda g: g.fitness)
        if best.fitness > self.best_fitness:
            self.best_fitness = best.fitness
            self.best_genome = best
            print(f"\n[NEW BEST] Fitness: {best.fitness:.2f} | W/L: {best.wins}/{best.losses}")
        
        # Selection
        print(f"\n[SELECT] Selecting top {self.elite_size} genomes...")
        elites = self.selection()
        
        # Print elite stats
        print(f"\n{'─'*70}")
        print("ELITE GENOMES:")
        for i, elite in enumerate(elites[:5]):  # Show top 5
            print(f"  #{i+1}: Fitness={elite.fitness:.2f} | "
                  f"W/L={elite.wins}/{elite.losses} ({elite.win_rate:.1%}) | "
                  f"Aggression={elite.genes['aggression_threshold']:.1f}")
        print(f"{'─'*70}")
        
        # Crossover and mutation
        print(f"\n[BREED] Creating {self.population_size - self.elite_size} offspring...")
        self.population = self.crossover_and_mutate(elites)
        
        # Save best genome
        self.save_best_genome()
        
        # Save generation stats
        self.save_generation_stats()
        
        self.generation += 1
        
        print(f"\nGeneration {self.generation - 1} complete!")
        print(f"Time: {time.time() - start_time:.1f}s")
    
    def save_best_genome(self):
        """Save best genome to file"""
        if self.best_genome:
            # Save generation-specific snapshot
            filename = f"best_genome_gen{self.generation}.json"
            filepath = os.path.join(self.genomes_dir, filename)
            self.best_genome.save(filepath)
            
            # Also save as "best_genome.json" for easy loading
            current_best = os.path.join(self.genomes_dir, "best_genome.json")
            self.best_genome.save(current_best)
            
            print(f"\n[SAVE] Best genome saved to: {self.genomes_dir}/{filename}")
    
    def save_generation_stats(self):
        """Save generation statistics"""
        stats = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'population_size': self.population_size,
            'elite_size': self.elite_size,
            'avg_fitness': sum(g.fitness for g in self.population) / len(self.population),
            'min_fitness': min(g.fitness for g in self.population),
            'max_fitness': max(g.fitness for g in self.population),
        }
        
        # Append to stats file in evolved_genomes folder
        stats_file = os.path.join(self.genomes_dir, "evolution_stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                all_stats = json.load(f)
        else:
            all_stats = []
        
        all_stats.append(stats)
        
        with open(stats_file, 'w') as f:
            json.dump(all_stats, f, indent=2)
    
    def run(self, num_generations=10):
        """
        Run evolution for multiple generations.
        
        Args:
            num_generations: Number of generations to evolve
        """
        print(f"\n[START] Running evolution for {num_generations} generations...")
        
        overall_start = time.time()
        
        for gen in range(num_generations):
            self.evolve_generation()
        
        total_time = time.time() - overall_start
        
        print(f"\n{'='*70}")
        print("EVOLUTION COMPLETE!")
        print(f"{'='*70}")
        print(f"Total Time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
        print(f"Best Fitness: {self.best_fitness:.2f}")
        print(f"\nBest genome saved to: {self.genomes_dir}/best_genome.json")
        print(f"Load it with: genome = FuzzyGenome.load('{self.genomes_dir}/best_genome.json')")
        
        if self.best_genome:
            print(self.best_genome.get_summary())


def main():
    """Main training loop"""
    print("\n" + "="*70)
    print("FUZZY AI GENETIC ALGORITHM TRAINER")
    print("="*70)
    
    # Configuration
    POPULATION_SIZE = 25
    ELITE_SIZE = 5
    NUM_GENERATIONS = 25
    TOURNAMENT_SIZE = 5  # Each bot fights only 2 opponents per generation

    print(f"\nConfiguration:")
    print(f"  Population: {POPULATION_SIZE} bots")
    print(f"  Elites: {ELITE_SIZE} best bots kept each generation")
    print(f"  Generations: {NUM_GENERATIONS}")
    print(f"  Matches per bot: {TOURNAMENT_SIZE} (tournament size)")
    print(f"  Total matches: ~{POPULATION_SIZE * TOURNAMENT_SIZE * NUM_GENERATIONS}")

    input("\nPress ENTER to start evolution...")

    # Create trainer
    trainer = GeneticTrainer(
        population_size=POPULATION_SIZE,
        elite_size=ELITE_SIZE
    )
    trainer.tournament_size = TOURNAMENT_SIZE  # Set tournament size

    # Initialize population
    trainer.initialize_population()
    
    # Run evolution
    trainer.run(num_generations=NUM_GENERATIONS)
    
    print(f"\nTraining complete! Check evolved_genomes/best_genome.json for the evolved bot.")


if __name__ == "__main__":
    main()
