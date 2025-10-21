"""
Visualize the evolution progress from training data.
Shows fitness trends, parameter evolution, and genome comparisons.
"""

import os
import json
import sys

def load_evolution_stats():
    """Load evolution statistics from evolved_genomes folder"""
    stats_file = os.path.join("evolved_genomes", "evolution_stats.json")
    
    if not os.path.exists(stats_file):
        print(f"Error: {stats_file} not found!")
        print("Run ga_trainer.py first to generate evolution data.")
        return None
    
    with open(stats_file, 'r') as f:
        return json.load(f)

def load_genome(filename):
    """Load a specific genome file"""
    filepath = os.path.join("evolved_genomes", filename)
    
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)

def print_fitness_chart(stats):
    """Print ASCII chart of fitness progression"""
    print("\n" + "="*70)
    print("FITNESS PROGRESSION")
    print("="*70)
    
    generations = [s['generation'] for s in stats]
    best_fitness = [s['best_fitness'] for s in stats]
    avg_fitness = [s['avg_fitness'] for s in stats]
    
    # Find min/max for scaling
    all_values = best_fitness + avg_fitness
    min_val = min(all_values)
    max_val = max(all_values)
    
    if max_val == min_val:
        max_val = min_val + 1
    
    print(f"\nGen | Best Fitness | Avg Fitness | Chart (Best=*, Avg=.)")
    print("-" * 70)
    
    for i, gen in enumerate(generations):
        best = best_fitness[i]
        avg = avg_fitness[i]
        
        # Scale to 40 character width
        best_pos = int((best - min_val) / (max_val - min_val) * 40)
        avg_pos = int((avg - min_val) / (max_val - min_val) * 40)
        
        # Create chart line
        chart = [' '] * 41
        chart[avg_pos] = '.'
        chart[best_pos] = '*'
        
        print(f"{gen:3d} | {best:10.2f}   | {avg:10.2f}  | {''.join(chart)}")
    
    print(f"\nImprovement: {best_fitness[0]:.2f} → {best_fitness[-1]:.2f} (+{best_fitness[-1] - best_fitness[0]:.2f})")

def print_statistics_table(stats):
    """Print detailed statistics table"""
    print("\n" + "="*70)
    print("GENERATION STATISTICS")
    print("="*70)
    
    print(f"\n{'Gen':<5} {'Best':<10} {'Avg':<10} {'Min':<10} {'Max':<10}")
    print("-" * 70)
    
    for s in stats:
        print(f"{s['generation']:<5} {s['best_fitness']:<10.2f} {s['avg_fitness']:<10.2f} "
              f"{s['min_fitness']:<10.2f} {s['max_fitness']:<10.2f}")

def compare_genomes(gen1, gen2):
    """Compare two genome generations"""
    genome1 = load_genome(f"best_genome_gen{gen1}.json")
    genome2 = load_genome(f"best_genome_gen{gen2}.json")
    
    if not genome1 or not genome2:
        print(f"\nError: Could not load genomes for generations {gen1} and {gen2}")
        return
    
    print("\n" + "="*70)
    print(f"GENOME COMPARISON: Gen {gen1} vs Gen {gen2}")
    print("="*70)
    
    print(f"\nFitness: {genome1['fitness']:.2f} → {genome2['fitness']:.2f} "
          f"(change: {genome2['fitness'] - genome1['fitness']:+.2f})")
    print(f"W/L: {genome1['wins']}/{genome1['losses']} → {genome2['wins']}/{genome2['losses']}")
    
    print(f"\n{'Parameter':<30} {'Gen ' + str(gen1):<12} {'Gen ' + str(gen2):<12} {'Change':<12}")
    print("-" * 70)
    
    genes1 = genome1['genes']
    genes2 = genome2['genes']
    
    for param in sorted(genes1.keys()):
        val1 = genes1[param]
        val2 = genes2[param]
        change = val2 - val1
        change_str = f"{change:+.2f}" if abs(change) > 0.01 else "~"
        
        print(f"{param:<30} {val1:<12.2f} {val2:<12.2f} {change_str:<12}")

def print_parameter_evolution(stats, param_name):
    """Show how a specific parameter evolved"""
    print("\n" + "="*70)
    print(f"PARAMETER EVOLUTION: {param_name}")
    print("="*70)
    
    values = []
    for s in stats:
        gen = s['generation']
        genome = load_genome(f"best_genome_gen{gen}.json")
        if genome and param_name in genome['genes']:
            values.append(genome['genes'][param_name])
        else:
            values.append(None)
    
    if not any(values):
        print("Parameter not found in genomes.")
        return
    
    # Filter out None values
    valid_values = [v for v in values if v is not None]
    min_val = min(valid_values)
    max_val = max(valid_values)
    
    if max_val == min_val:
        max_val = min_val + 1
    
    print(f"\nGen | Value      | Chart")
    print("-" * 70)
    
    for i, val in enumerate(values):
        if val is None:
            continue
        
        gen = stats[i]['generation']
        pos = int((val - min_val) / (max_val - min_val) * 40)
        chart = ' ' * pos + '*'
        
        print(f"{gen:3d} | {val:10.2f} | {chart}")
    
    print(f"\nRange: {min_val:.2f} to {max_val:.2f} (change: {valid_values[-1] - valid_values[0]:+.2f})")

def main():
    print("="*70)
    print("GENETIC ALGORITHM EVOLUTION VISUALIZER")
    print("="*70)
    
    # Load stats
    stats = load_evolution_stats()
    if not stats:
        return
    
    print(f"\nLoaded {len(stats)} generations of evolution data")
    
    # Show menu
    while True:
        print("\n" + "="*70)
        print("OPTIONS:")
        print("="*70)
        print("1. Show fitness progression chart")
        print("2. Show generation statistics table")
        print("3. Compare two generations")
        print("4. Show parameter evolution")
        print("5. Show all visualizations")
        print("0. Exit")
        print("="*70)
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            print_fitness_chart(stats)
        
        elif choice == '2':
            print_statistics_table(stats)
        
        elif choice == '3':
            try:
                gen1 = int(input("Enter first generation number: "))
                gen2 = int(input("Enter second generation number: "))
                compare_genomes(gen1, gen2)
            except ValueError:
                print("Invalid input. Please enter numbers.")
        
        elif choice == '4':
            print("\nAvailable parameters:")
            genome = load_genome("best_genome_gen1.json")
            if genome:
                params = sorted(genome['genes'].keys())
                for i, p in enumerate(params, 1):
                    print(f"  {i}. {p}")
                
                try:
                    idx = int(input("\nEnter parameter number: ")) - 1
                    if 0 <= idx < len(params):
                        print_parameter_evolution(stats, params[idx])
                    else:
                        print("Invalid parameter number.")
                except ValueError:
                    print("Invalid input.")
        
        elif choice == '5':
            print_fitness_chart(stats)
            print_statistics_table(stats)
            
            # Compare first and last generation
            first_gen = stats[0]['generation']
            last_gen = stats[-1]['generation']
            compare_genomes(first_gen, last_gen)
        
        elif choice == '0':
            print("\nExiting...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
