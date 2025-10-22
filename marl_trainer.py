"""
MARL Trainer for Gun Mayhem using PPO and Self-Play.

This script trains one PPO model and makes it play against
a frozen copy of itself, updating the opponent periodically.
"""
import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback
from marl_environment import GunMayhemEnv

# --- Configuration ---
TOTAL_TIMESTEPS = 2_000_000  # Total steps to train for
STEPS_PER_UPDATE = 100_000    # Steps to train before updating the opponent
MODEL_NAME = "ppo_gunmayhem_marl"
LOG_DIR = "logs_marl"
MODEL_DIR = "models_marl"
OPPONENT_PATH = os.path.join(MODEL_DIR, "best_opponent.zip")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# Policy network architecture
# We use a small network (16 units) similar to your neural_ai.py
policy_kwargs = dict(
    net_arch=dict(pi=[16], vf=[16]) # pi = policy, vf = value function
)

def create_environment(opponent_model=None):
    """Helper function to create and wrap the environment."""
    env = GunMayhemEnv(opponent_model=opponent_model)
    env = DummyVecEnv([lambda: env])
    return env

def main():
    print("="*60)
    print("MARL (PPO Self-Play) Trainer")
    print("="*60)
    
    # 1. Create a dummy model to start
    if not os.path.exists(OPPONENT_PATH):
        print("No opponent model found. Creating a new one...")
        # Create a temporary env with no opponent
        temp_env = create_environment(opponent_model=None)
        # Create a new model with small network
        initial_model = PPO(
            "MlpPolicy", 
            temp_env, 
            policy_kwargs=policy_kwargs, 
            verbose=1, 
            tensorboard_log=LOG_DIR
        )
        initial_model.save(OPPONENT_PATH)
        temp_env.close()
        del temp_env
        del initial_model
        print(f"Initial opponent model saved to {OPPONENT_PATH}")

    # 2. Load the initial opponent
    opponent_model = PPO.load(OPPONENT_PATH)
    
    # 3. Create the main environment
    env = create_environment(opponent_model=opponent_model)
    
    # 4. Load the main model (or create new)
    if os.path.exists(os.path.join(MODEL_DIR, f"{MODEL_NAME}.zip")):
        print("Loading existing model...")
        model = PPO.load(
            os.path.join(MODEL_DIR, f"{MODEL_NAME}.zip"), 
            env=env
        )
        model.set_tensorboard_log(LOG_DIR)
    else:
        print("Creating new model...")
        model = PPO(
            "MlpPolicy",
            env,
            policy_kwargs=policy_kwargs,
            verbose=1,
            tensorboard_log=LOG_DIR,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            learning_rate=3e-4
        )

    # 5. The Self-Play Training Loop
    num_updates = TOTAL_TIMESTEPS // STEPS_PER_UPDATE
    print(f"Starting training for {TOTAL_TIMESTEPS} steps ({num_updates} updates)...")
    
    for i in range(num_updates):
        print(f"\n---=== Update {i+1} / {num_updates} ===---")
        start_time = time.time()
        
        # Train the model
        model.learn(
            total_timesteps=STEPS_PER_UPDATE,
            reset_num_timesteps=False,  # Continue counting
            tb_log_name=MODEL_NAME
        )
        
        # Save the newly trained model
        model.save(os.path.join(MODEL_DIR, MODEL_NAME))
        print("Model saved.")
        
        # Update the opponent
        print("Updating opponent model...")
        opponent_model.load(os.path.join(MODEL_DIR, f"{MODEL_NAME}.zip"))
        
        # Set the environment's opponent to the new model
        # We must use the 'env.envs[0]' because it's wrapped by DummyVecEnv
        env.envs[0].set_opponent_model(opponent_model)
        
        end_time = time.time()
        print(f"Update {i+1} finished in {(end_time - start_time) / 60:.2f} minutes.")

    print("="*60)
    print("Training Complete!")
    print(f"Final model saved to: {MODEL_DIR}/{MODEL_NAME}.zip")
    print("Run 'tensorboard --logdir=logs_marl' to see results.")
    print("="*60)
    
    env.close()

if __name__ == "__main__":
    main()