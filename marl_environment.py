"""
Gym Environment Wrapper for Gun Mayhem for MARL training.

This environment implements a self-play scenario.
- The 'agent' (Agent 0) is the one being trained.
- The 'opponent' (Agent 1) uses a provided policy model.
"""
import os
import sys
import gym
import time
import numpy as np
from gym import spaces
from typing import Optional, Dict

# Add DLL paths (copied from your scripts)
dll_paths = [
    r"C:\mingw64\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2-2.32.8\x86_664-w64-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\libs\SDL2_ttf-2.24.0\x86_64-w64-mingw32\bin",
    r"C:\Users\jayad\Desktop\PROJECTS\Gun-Mayhem\build_pybind"
]
if sys.version_info >= (3, 8):
    for path in dll_paths:
        if os.path.exists(path):
            os.add_dll_directory(path)

import gunmayhem
from stable_baselines3.common.base_class import BaseAlgorithm
from feature_extraction import get_observation, INPUT_SIZE

# Constants
MAX_FRAMES = 3600  # 60 seconds at 60fps

class GunMayhemEnv(gym.Env):
    """
    Gun Mayhem Gym Environment for Self-Play MARL.
    
    Action Space: MultiBinary(6) -> [up, left, down, right, primary, secondary]
    Observation Space: Box(12) -> Features from feature_extraction.py
    """
    metadata = {'render.modes': ['human']}

    def __init__(self, opponent_model: Optional[BaseAlgorithm] = None):
        super(GunMayhemEnv, self).__init__()

        self.game = None
        self.game_state = None
        self.game_control = None
        
        # Define action and observation spaces
        # 6 boolean actions
        self.action_space = spaces.MultiBinary(6)
        # 12 continuous features
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(INPUT_SIZE,), dtype=np.float32
        )

        self.opponent_model = opponent_model
        
        # State tracking for rewards
        self.last_p1_health = 100.0
        self.last_p1_lives = 3
        self.last_p2_health = 100.0
        self.last_p2_lives = 3
        
        self.frame_count = 0
        self.p1_id = None
        self.p2_id = None
        
        # Change to build directory (required by your scripts)
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.build_dir = os.path.join(project_root, 'build')
        self.original_dir = os.getcwd()
        os.makedirs(self.build_dir, exist_ok=True)

    def set_opponent_model(self, opponent_model: BaseAlgorithm):
        """Updates the opponent policy."""
        self.opponent_model = opponent_model

    def _get_game_state(self) -> Optional[Dict]:
        """Gets the player states from the game."""
        if not self.game or not self.game.is_running():
            return None, None
            
        players = self.game_state.get_all_players()
        if len(players) < 2:
            return None, None
            
        if self.p1_id is None:
            self.p1_id, self.p2_id = list(players.keys())[:2]
            
        p1 = players.get(self.p1_id)
        p2 = players.get(self.p2_id)
        
        if not p1 or not p2:
            return None, None
            
        return p1, p2

    def _compute_reward(self, p1_state, p2_state) -> (float, bool):
        """
        Calculates the step reward and done flag.
        """
        reward = 0.0
        done = False
        
        # Health change reward
        damage_dealt = (self.last_p2_health - p2_state['health'])
        damage_taken = (self.last_p1_health - p1_state['health'])
        
        reward += damage_dealt * 0.1  # Reward for dealing damage
        reward -= damage_taken * 0.1  # Penalize for taking damage

        # Life change reward
        if p2_state['lives'] < self.last_p2_lives:
            reward += 10.0  # Big reward for taking a life
        if p1_state['lives'] < self.last_p1_lives:
            reward -= 10.0  # Big penalty for losing a life

        # Update last state
        self.last_p1_health = p1_state['health']
        self.last_p2_health = p2_state['health']
        self.last_p1_lives = p1_state['lives']
        self.last_p2_lives = p2_state['lives']

        # Check for game over
        if p1_state['lives'] <= 0:
            reward -= 100.0  # Big loss penalty
            done = True
        elif p2_state['lives'] <= 0:
            reward += 100.0  # Big win bonus
            done = True
        elif self.frame_count >= MAX_FRAMES:
            done = True # Timeout
            
        return reward, done

    def _convert_action(self, action_array) -> Dict:
        """Converts MultiBinary array [0,1,0,1,1,0] to action dict."""
        return {
            'up': bool(action_array[0]),
            'left': bool(action_array[1]),
            'down': bool(action_array[2]),
            'right': bool(action_array[3]),
            'primaryFire': bool(action_array[4]),
            'secondaryFire': bool(action_array[5]),
        }

    def step(self, action_p1):
        """
        Run one timestep of the environment's dynamics.
        """
        os.chdir(self.build_dir)
        
        try:
            # 1. Get observation for opponent
            p1_state, p2_state = self._get_game_state()
            if p1_state is None:
                # Game crashed or ended unexpectedly
                os.chdir(self.original_dir)
                return self.observation_space.sample(), -100, True, {}

            obs_p2 = get_observation(p2_state, p1_state) # Note: reversed!
            
            # 2. Get actions for both players
            action_p1_dict = self._convert_action(action_p1)
            
            if self.opponent_model:
                action_p2_array, _ = self.opponent_model.predict(obs_p2, deterministic=True)
                action_p2_dict = self._convert_action(action_p2_array)
            else:
                # Dummy opponent does nothing
                action_p2_dict = self._convert_action(np.zeros(6))

            # 3. Apply actions
            # self.game_control.set_player_movement(self.p1_id, **action_p1_dict)
            # self.game_control.set_player_movement(self.p2_id, **action_p2_dict)

            self.game_control.set_player_movement(
                self.p1_id, 
                action_p1_dict['up'],
                action_p1_dict['left'],
                action_p1_dict['down'],
                action_p1_dict['right'],
                action_p1_dict['primaryFire'],
                action_p1_dict['secondaryFire']
            )
            self.game_control.set_player_movement(
                self.p2_id, 
                action_p2_dict['up'],
                action_p2_dict['left'],
                action_p2_dict['down'],
                action_p2_dict['right'],
                action_p2_dict['primaryFire'],
                action_p2_dict['secondaryFire']
            )

            # 4. Step the game
            self.game.update(0.0166) # Assuming 60fps
            self.frame_count += 1
            
            # 5. Get new state
            new_p1_state, new_p2_state = self._get_game_state()
            if new_p1_state is None:
                os.chdir(self.original_dir)
                return self.observation_space.sample(), -100, True, {} # Error

            # 6. Compute reward and done
            reward, done = self._compute_reward(new_p1_state, new_p2_state)

            # 7. Get new observation for P1
            obs_p1 = get_observation(new_p1_state, new_p2_state)
            
            os.chdir(self.original_dir)
            return obs_p1, reward, done, {}

        except Exception as e:
            print(f"[ENV_ERROR] Exception in step: {e}")
            self.close()
            os.chdir(self.original_dir)
            # On error, end the episode with a large penalty
            return self.observation_space.sample(), -200, True, {}

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        """
        self.close() # Close any existing game
        os.chdir(self.build_dir)
        
        try:
            self.game = gunmayhem.GameRunner()
            if not self.game.init_game("MARL Training"):
                raise Exception("Failed to initialize game")
            
            self.game_state = gunmayhem.GameState()
            self.game_control = gunmayhem.GameControl()

            # Wait for game to be ready and get player IDs
            p1, p2 = None, None
            for _ in range(10): # Wait up to 10 frames
                self.game.handle_events()
                self.game.update(0.0166)
                p1, p2 = self._get_game_state()
                if p1 and p2:
                    break
                time.sleep(0.01)

            if not p1 or not p2:
                raise Exception("Game state not ready after reset")
            
            # Disable keyboard
            self.game_control.disable_keyboard_for_player(self.p1_id)
            self.game_control.disable_keyboard_for_player(self.p2_id)
            
            # Reset state trackers
            self.last_p1_health = p1['health']
            self.last_p1_lives = p1['lives']
            self.last_p2_health = p2['health']
            self.last_p2_lives = p2['lives']
            self.frame_count = 0
            
            os.chdir(self.original_dir)
            
            # Return the initial observation
            return get_observation(p1, p2)

        except Exception as e:
            print(f"[ENV_ERROR] Exception in reset: {e}")
            self.close()
            os.chdir(self.original_dir)
            # If reset fails, we can't continue.
            # A common trick is to return a valid observation and end immediately.
            # But here, we'll just return a dummy observation.
            return self.observation_space.sample()

    def render(self, mode='human'):
        """Renders the environment."""
        if self.game and self.game.is_running():
            self.game.render()
        else:
            print("Cannot render: Game is not running.")

    def close(self):
        """Cleans up the environment."""
        if self.game:
            try:
                self.game.quit()
            except Exception as e:
                print(f"[ENV_WARN] Exception in game.quit(): {e}")
        self.game = None
        self.game_state = None
        self.game_control = None
        self.p1_id = None
        self.p2_id = None