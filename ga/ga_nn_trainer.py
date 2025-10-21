"""
GA trainer for neural-network-controlled bots.
Very similar to ga_trainer.py but uses NeuralGenome + NeuralAI and saves to evolved_nn/.
"""
import os
import sys
import time
import random
import json
from typing import List, Tuple

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

# Ensure project root on path when running this module directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import gunmayhem
from ga.neural_genome import NeuralGenome
from nn.neural_ai import NeuralAI


class NeuralGATrainer:
    def __init__(self, population_size=5, elite_size=2, tournament_size=2):
        self.population_size = population_size
        self.elite_size = elite_size
        self.tournament_size = tournament_size
        self.population: List[NeuralGenome] = []
        self.generation = 0
        self.best_genome = None
        self.best_fitness = 0.0
        # artifacts dir
        self.out_dir = "evolved_nn"
        os.makedirs(self.out_dir, exist_ok=True)
        print("="*70)
        print("NEURAL GA TRAINER")
        print("="*70)
        print(f"Population: {population_size} | Elites: {elite_size} | Matches/bot: {tournament_size}")

    def initialize_population(self):
        self.population = [NeuralGenome() for _ in range(self.population_size)]

    def _play_match(self, g1: NeuralGenome, g2: NeuralGenome, max_frames=1800, headless=True) -> Tuple[str, dict]:
        # Change to build directory at repo root so ../assets resolves correctly
        build_dir = os.path.join(PROJECT_ROOT, 'build')
        os.makedirs(build_dir, exist_ok=True)
        original_dir = os.getcwd()
        os.chdir(build_dir)
        try:
            game = gunmayhem.GameRunner()
            if not game.init_game("GA NN - Bot vs Bot"):
                os.chdir(original_dir)
                return 'draw', {}
            ai1 = NeuralAI(g1)
            ai2 = NeuralAI(g2)
            game_state = gunmayhem.GameState()
            game_control = gunmayhem.GameControl()
            frame = 0
            disabled = False
            while game.is_running() and frame < max_frames:
                game.handle_events()
                players = game_state.get_all_players()
                if len(players) >= 2:
                    pids = list(players.keys())
                    if not disabled:
                        game_control.disable_keyboard_for_player(pids[0])
                        game_control.disable_keyboard_for_player(pids[1])
                        disabled = True
                    p1 = players[pids[0]]
                    p2 = players[pids[1]]
                    # win checks
                    if p2['lives'] <= 0:
                        game.quit(); os.chdir(original_dir)
                        return 'player1', {'frames': frame, 'winner_health': p1['health'], 'winner_lives': p1['lives']}
                    if p1['lives'] <= 0:
                        game.quit(); os.chdir(original_dir)
                        return 'player2', {'frames': frame, 'winner_health': p2['health'], 'winner_lives': p2['lives']}
                    a1 = ai1.decide_action(p1, p2)
                    a2 = ai2.decide_action(p2, p1)
                    game_control.set_player_movement(pids[0], bool(a1['up']), bool(a1['left']), bool(a1['down']), bool(a1['right']), bool(a1['primaryFire']), bool(a1['secondaryFire']))
                    game_control.set_player_movement(pids[1], bool(a2['up']), bool(a2['left']), bool(a2['down']), bool(a2['right']), bool(a2['primaryFire']), bool(a2['secondaryFire']))
                game.update(0.0166)
                if not headless:
                    game.render()
                frame += 1
            game.quit(); os.chdir(original_dir)
            return 'draw', {'frames': frame}
        except Exception as e:
            try:
                game.quit()
            except Exception:
                pass
            os.chdir(original_dir)
            return 'draw', {}

    def evaluate_fitness(self, genome: NeuralGenome, pool: List[NeuralGenome]) -> float:
        wins = 0; losses = 0; total = 0.0
        opponents = random.sample(pool, min(self.tournament_size, len(pool)))
        for opp in opponents:
            winner, stats = self._play_match(genome, opp, max_frames=1800, headless=True)
            if winner == 'player1':
                wins += 1
                speed_bonus = max(0, 1800 - stats.get('frames', 1800)) / 100
                health_bonus = stats.get('winner_health', 0) / 10
                lives_bonus = stats.get('winner_lives', 0) * 50
                total += 100 + speed_bonus + health_bonus + lives_bonus
            elif winner == 'player2':
                losses += 1
            else:
                total += 25
        genome.wins = wins; genome.losses = losses; genome.matches_played = len(opponents)
        genome.fitness = total / max(1, len(opponents))
        return genome.fitness

    def selection(self) -> List[NeuralGenome]:
        return sorted(self.population, key=lambda g: g.fitness, reverse=True)[:self.elite_size]

    def crossover_and_mutate(self, elites: List[NeuralGenome]) -> List[NeuralGenome]:
        new_pop = elites.copy()
        while len(new_pop) < self.population_size:
            p1, p2 = random.sample(elites, 2)
            child = p1.crossover(p2)
            child.mutate(mutation_rate=0.15, sigma=0.1)
            new_pop.append(child)
        return new_pop

    def save_best(self):
        if not self.population:
            return
        best = max(self.population, key=lambda g: g.fitness)
        if best.fitness > self.best_fitness:
            self.best_fitness = best.fitness
            self.best_genome = best
        if self.best_genome:
            gen_file = os.path.join(self.out_dir, f"best_genome_gen{self.generation}.json")
            cur_file = os.path.join(self.out_dir, "best_genome.json")
            self.best_genome.save(gen_file)
            self.best_genome.save(cur_file)
            print(f"[SAVE] {gen_file}")

    def save_stats(self):
        stats_file = os.path.join(self.out_dir, "evolution_stats.json")
        row = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'avg_fitness': sum(g.fitness for g in self.population)/len(self.population),
            'min_fitness': min(g.fitness for g in self.population),
            'max_fitness': max(g.fitness for g in self.population),
            'population': self.population_size,
            'elites': self.elite_size,
            'tournament': self.tournament_size,
        }
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        data.append(row)
        with open(stats_file, 'w') as f:
            json.dump(data, f, indent=2)

    def evolve_generation(self):
        print(f"\n=== GENERATION {self.generation} ===")
        start = time.time()
        for i, g in enumerate(self.population):
            pool = [x for x in self.population if x is not g]
            fit = self.evaluate_fitness(g, pool)
            print(f"  [{i+1}/{len(self.population)}] fitness={fit:.2f}")
        elites = self.selection()
        self.population = self.crossover_and_mutate(elites)
        self.save_best(); self.save_stats()
        self.generation += 1
        print(f"Gen time: {time.time()-start:.1f}s")

    def run(self, generations=3):
        print(f"Starting NN evolution for {generations} generations...")
        for _ in range(generations):
            self.evolve_generation()
        print(f"Done. Best fitness={self.best_fitness:.2f}. Artifacts in {self.out_dir}/")


def main():
    POP = 5; ELITE = 2; TOUR = 2; GENS = 3
    print("\nNN GA Trainer Config:")
    print(f"  Population={POP}  Elites={ELITE}  Matches/bot={TOUR}  Generations={GENS}")
    input("\nPress ENTER to start NN evolution...")
    trainer = NeuralGATrainer(POP, ELITE, TOUR)
    trainer.initialize_population()
    trainer.run(generations=GENS)


if __name__ == "__main__":
    main()
