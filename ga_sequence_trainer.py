"""
GA Trainer for Action Sequence Optimization.

This bot evolves a fixed 10-second sequence of actions (a "script")
to maximize damage against a static 10-second recording of a
human player.
"""
import os
import sys
import time
import json
import random
from typing import List, Tuple, Dict

# Add DLL paths
dll_paths = [
    r"C:\mingw64\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2-2.32.8\x86_64-w664-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2_ttf-2.24.0\x86_64-w664-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\build_pybind"
]
if sys.version_info >= (3, 8):
    for path in dll_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)

import gunmayhem
from sequence_genome import SequenceGenome, TOTAL_FRAMES, NUM_WINDOWS

# --- Configuration ---
RECORDING_FILE = "my_recording.json"
POPULATION_SIZE = 50
ELITE_SIZE = 5
NUM_GENERATIONS = 100
# ---

class SequenceGATrainer:
    def __init__(self):
        self.generation = 0
        self.recording = self._load_recording()
        
        self.out_dir = "evolved_sequence"
        os.makedirs(self.out_dir, exist_ok=True)
        
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.build_dir = os.path.join(project_root, 'build')
        self.original_dir = os.getcwd()
        os.makedirs(self.build_dir, exist_ok=True)
        
        # --- NEW: Seed the population with new 3-int genome ---
        print("Creating initial population with seeds...")
        self.population = []

        # Seed 1: The "Stand Still" bot
        # horizontal: 2=None, vertical: 2=None, shoot: 2=None
        still_chunk = {'horizontal': 2, 'vertical': 2, 'shoot': 2}
        self.population.append(SequenceGenome(genes=[still_chunk] * NUM_WINDOWS))

        # Seed 2: The "Shoot Right" bot
        # horizontal: 1=Right, vertical: 2=None, shoot: 0=Primary
        shoot_chunk = {'horizontal': 1, 'vertical': 2, 'shoot': 0}
        self.population.append(SequenceGenome(genes=[shoot_chunk] * NUM_WINDOWS))
        
        # Fill the rest with random bots
        while len(self.population) < POPULATION_SIZE:
            self.population.append(SequenceGenome())
        # ---
        
        print("="*60)
        print("GA Sequence Trainer")
        print(f"Population: {POPULATION_SIZE} (seeded) | Elites: {ELITE_SIZE}")
        print(f"Opponent: {RECORDING_FILE}")
        print("="*60)
        
    def _load_recording(self):
        try:
            with open(RECORDING_FILE, 'r') as f:
                rec = json.load(f)
            if len(rec) < TOTAL_FRAMES:
                raise Exception(f"Recording is too short! Expected {TOTAL_FRAMES} frames, got {len(rec)}")
            print(f"Loaded recording with {len(rec)} frames.")
            return rec
        except Exception as e:
            print(f"FATAL: Could not load {RECORDING_FILE}: {e}")
            print("Please run 'record_gameplay.py' first.")
            sys.exit(1)

    def _translate_genome_to_action(self, int_dict: Dict[str, int]) -> Dict[str, bool]:
        """
        Converts the 3-integer genome chunk into the 6-boolean
        action dictionary required by the game.
        """
        h = int_dict['horizontal']
        v = int_dict['vertical']
        s = int_dict['shoot']

        return {
            'up': (v == 0),
            'left': (h == 0),
            'down': (v == 1),
            'right': (h == 1),
            'primaryFire': (s == 0),
            'secondaryFire': (s == 1)
        }

    def _play_match_vs_recording(self, genome: SequenceGenome) -> float:
        """
        Plays one headless match: GA Bot (P1) vs Recording (P2).
        Returns the fitness score.
        """
        os.chdir(self.build_dir)
        
        try:
            game = gunmayhem.GameRunner()
            if not game.init_game("GA Sequence Training"):
                os.chdir(self.original_dir)
                return -1000.0 # Failed to init

            game_state = gunmayhem.GameState()
            game_control = gunmayhem.GameControl()
            
            p1_id, p2_id = None, None
            
            min_distance = 10000.0 
            
            for frame in range(TOTAL_FRAMES):
                if not game.is_running():
                    break 
                    
                game.handle_events()
                players = game_state.get_all_players()
                
                if len(players) < 2:
                    game.update(0.0166)
                    continue

                if p1_id is None:
                    p1_id, p2_id = list(players.keys())[:2]
                    game_control.disable_keyboard_for_player(p1_id)
                    game_control.disable_keyboard_for_player(p2_id)

                p1_state = players.get(p1_id)
                p2_state = players.get(p2_id)

                if not p1_state or not p2_state:
                    break 
                    
                if p1_state['lives'] <= 0 or p2_state['lives'] <= 0:
                    break 
                
                dist = abs(p1_state['x'] - p2_state['x']) + abs(p1_state['y'] - p2_state['y'])
                min_distance = min(min_distance, dist)
                
                # --- ACTION TRANSLATION ---
                # 1. Get the 3-integer action from the genome
                action_p1_int = genome.get_action_for_frame(frame)
                # 2. Translate it to the 6-boolean dictionary
                action_p1_bool = self._translate_genome_to_action(action_p1_int)
                # 3. Get the opponent's action (already in 6-boolean format)
                action_p2 = self.recording[frame] 
                
                # Apply actions
                game_control.set_player_movement(
                    p1_id, action_p1_bool['up'], action_p1_bool['left'], action_p1_bool['down'],
                    action_p1_bool['right'], action_p1_bool['primaryFire'], action_p1_bool['secondaryFire']
                )
                game_control.set_player_movement(
                    p2_id, action_p2['up'], action_p2['left'], action_p2['down'],
                    action_p2['right'], action_p2['primaryFire'], action_p2['secondaryFire']
                )
                # ---
                
                game.update(0.0166)
            
            players = game_state.get_all_players()
            p1_final = players.get(p1_id, {'health': 0, 'lives': 0})
            p2_final = players.get(p2_id, {'health': 0, 'lives': 0})
            
            p1_health_lost = (10 - p1_final['lives']) * 100 + (100 - p1_final['health'])
            p2_health_lost = (10 - p2_final['lives']) * 100 + (100 - p2_final['health'])

            fitness = (p2_health_lost - p1_health_lost) * 10 + (1000 - min_distance)

            game.quit()
            os.chdir(self.original_dir)
            return fitness

        except Exception as e:
            print(f"[ERROR] Match failed: {e}")
            try:
                game.quit()
            except: pass
            os.chdir(self.original_dir)
            return -1000.0

    def run(self, generations=NUM_GENERATIONS):
        print(f"Running evolution for {generations} generations...")
        best_fitness = -float('inf')
        
        for gen in range(generations):
            start_time = time.time()
            
            for genome in self.population:
                genome.fitness = self._play_match_vs_recording(genome)
            
            sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
            elites = sorted_pop[:ELITE_SIZE]
            best_of_gen = elites[0]
            
            if best_of_gen.fitness > best_fitness:
                best_fitness = best_of_gen.fitness
                print(f"[NEW BEST] Gen {gen}: Fitness = {best_fitness:.2f}")

            best_of_gen.save(os.path.join(self.out_dir, "best_genome.json"))
            
            new_population = elites.copy()
            while len(new_population) < POPULATION_SIZE:
                p1, p2 = random.sample(elites, 2)
                child = p1.crossover(p2)
                child.mutate(mutation_rate=0.1) 
                new_population.append(child)
                
            self.population = new_population
            gen_time = time.time() - start_time
            print(f"Gen {gen} complete in {gen_time:.2f}s. Best Fitness: {best_of_gen.fitness:.2f}. (Best bot saved)")
            
        print("\nEvolution complete!")
        print(f"Final best bot saved to {self.out_dir}/best_genome.json")

if __name__ == "__main__":
    trainer = SequenceGATrainer()
    trainer.run()