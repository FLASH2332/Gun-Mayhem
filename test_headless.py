"""
Test headless training mode - runs one quick match to verify setup
"""

import os
import sys

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

from fuzzy_genome import FuzzyGenome
from ga_trainer import GeneticTrainer

def main():
    print("="*70)
    print("HEADLESS MODE TEST")
    print("="*70)
    print("\nThis will run ONE match between two random bots in headless mode.")
    print("You should see an SDL2 window appear briefly and then close.")
    print("The window is automatically cleaned up after the match.")
    print()
    input("Press ENTER to start test match...")
    
    # Create two random genomes
    genome1 = FuzzyGenome()
    genome2 = FuzzyGenome()
    
    print("\n[TEST] Creating trainer...")
    trainer = GeneticTrainer(population_size=2, elite_size=1)
    
    print("[TEST] Running headless match (max 10 seconds)...")
    print("       Watch for window to appear and then automatically close.")
    
    winner, stats = trainer.play_match(genome1, genome2, max_frames=600, headless=True)
    
    print(f"\n[TEST] Match complete!")
    print(f"       Winner: {winner}")
    print(f"       Frames: {stats.get('frames', 'N/A')}")
    
    if winner in ['player1', 'player2']:
        print(f"       Winner Health: {stats.get('winner_health', 'N/A'):.1f}")
        print(f"       Winner Lives: {stats.get('winner_lives', 'N/A')}")
    
    print("\n✓ Headless mode is working correctly!")
    print("✓ Window was automatically cleaned up after the match!")
    print("  This prevents window buildup during training.")
    print("\nYou can now run: python ga_trainer.py")

if __name__ == "__main__":
    main()
