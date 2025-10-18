# Gun Mayhem - Python Bindings

## Overview

This project includes comprehensive Python bindings using **PyBind11**, enabling Python to control and interact with the C++ game engine. The architecture allows you to:

- **Run the game loop from Python** (no separate C++ process needed)
- **Read game state** (player positions, health, bullets, platforms, etc.)
- **Control players from Python** (including AI-controlled players)
- **Implement AI** using scikit-fuzzy, PyTorch, or any Python library
- **Mix human and AI players** in the same game

## Architecture

```
┌─────────────────────────────────────────┐
│         Python (play_vs_ai.py)          │
│  ┌───────────────────────────────────┐  │
│  │      Fuzzy AI (fuzzy_ai.py)       │  │
│  │  • SimpleFuzzyAI (fallback)       │  │
│  │  • FuzzyAI (scikit-fuzzy)         │  │
│  │  • Inputs: distance, health, pos  │  │
│  │  • Outputs: movement, shooting    │  │
│  └───────────────────────────────────┘  │
│               ▲         │               │
│               │ state   │ commands      │
│               │         ▼               │
│  ┌────────────┴──────────────────────┐  │
│  │   Python Bindings (gunmayhem.pyd) │  │
│  │  • GameRunner: init/update/render │  │
│  │  • GameState: read state          │  │
│  │  • GameControl: send commands     │  │
│  └────────────┬──────────────────────┘  │
└───────────────┼─────────────────────────┘
                │ PyBind11
┌───────────────┼─────────────────────────┐
│               ▼                         │
│      C++ Game Engine (SDL2)             │
│  • PlayState: game logic                │
│  • Player: movement, combat             │
│  • Bullet: projectile physics           │
│  • CollisionHandler: collisions         │
│  • TextureManager: rendering            │
└─────────────────────────────────────────┘
```

## Prerequisites

### C++ Build Tools
- **MinGW-w64** with GCC 13+ (download from [WinLibs](https://winlibs.com/))
- **CMake** 3.15+
- **SDL2** libraries (included in `libs/`)

### Python Requirements
```bash
# Core dependencies
pip install pybind11

# For AI functionality
pip install scikit-fuzzy numpy
```

## Building the Python Module

### Quick Build (Recommended)
```cmd
build_python_module.bat
```

This script:
1. Creates `build_pybind/` directory
2. Configures CMake with MinGW
3. Compiles C++ code with PyBind11
4. Copies the resulting `.pyd` module to project root

### Manual Build
```cmd
mkdir build_pybind
cd build_pybind
cmake .. -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
cmake --build . --config Release
copy gunmayhem.*.pyd ..
cd ..
```

### Build Output
- **Module**: `gunmayhem.cp313-win_amd64.pyd` (version may vary)
- **Size**: ~2-3 MB
- **Dependencies**: SDL2.dll, SDL2_ttf.dll (auto-loaded via os.add_dll_directory)

## Python Bindings API

### GameRunner
Controls the game loop from Python.

```python
import gunmayhem

game = gunmayhem.GameRunner()

# Initialize game window
game.init_game("Gun Mayhem - Human vs AI")  # Returns bool (success)

# Game loop
while game.is_running():
    game.handle_events()  # Process SDL events (keyboard, window)
    game.update(0.0166)   # Update game state (60 FPS = 0.0166s)
    game.render()         # Draw frame to screen
```

### GameState
Reads current game state without modifying it.

```python
game_state = gunmayhem.GameState()

# Get all players (returns dict)
players = game_state.get_all_players()
# Returns: {
#   "player_0": {
#       'id': 'player_0',
#       'health': 100.0,
#       'lives': 3,
#       'x': 400.0, 'y': 300.0,
#       'velocity_x': 0.0, 'velocity_y': 0.0,
#       'width': 32, 'height': 64,
#       'facing_direction': 1,  # 0=LEFT, 1=RIGHT
#       'collider_x': 400.0, 'collider_y': 300.0,
#       'collider_w': 32, 'collider_h': 64
#   },
#   "player_1": {...}
# }

# Get all bullets
bullets = game_state.get_all_bullets()
# Returns: {
#   "bullet_0": {
#       'id': 'bullet_0',
#       'owner_id': 'player_0',
#       'x': 450.0, 'y': 310.0,
#       'velocity_x': 15.0, 'velocity_y': 0.0,
#       'direction_x': 1.0, 'direction_y': 0.0,
#       'damage': 10.0,
#       'knockback': 5.0,
#       'expired': False
#   }
# }

# Get all platforms
platforms = game_state.get_all_platforms()
# Returns: {
#   "platform_0": {
#       'id': 'platform_0',
#       'x': 200.0, 'y': 500.0,
#       'width': 400, 'height': 20,
#       'collider_x': 200.0, 'collider_y': 500.0,
#       'collider_w': 400, 'collider_h': 20
#   }
# }

# Get game info
info = game_state.get_game_info()
# Returns: {
#   'screen_width': 1280,
#   'screen_height': 720
# }
```

### GameControl
Sends commands to control players.

```python
game_control = gunmayhem.GameControl()

# Control player movement (MUST use positional arguments)
game_control.set_player_movement(
    "player_1",    # player_id (string)
    True,          # up (jump)
    False,         # left
    False,         # down
    True,          # right
    True,          # primaryFire (shoot)
    False          # secondaryFire
)

# Disable keyboard input for AI-controlled player
game_control.disable_keyboard_for_player("player_1")
```

**Important:** Arguments must be **positional**, not keyword arguments. Use `bool()` to convert numpy booleans.

## Fuzzy AI Module (`fuzzy_ai.py`)

### SimpleFuzzyAI (Fallback)
Rule-based AI when scikit-fuzzy is unavailable.

```python
from fuzzy_ai import SimpleFuzzyAI

ai = SimpleFuzzyAI()

# Input: player state dictionaries
ai_state = players['player_1']
enemy_state = players['player_0']

# Get actions
actions = ai.decide_action(ai_state, enemy_state)
# Returns: {
#   'up': False,
#   'left': False,
#   'right': True,
#   'down': False,
#   'primaryFire': True,
#   'secondaryFire': False
# }
```

**Logic:**
- Moves towards enemy
- Jumps if enemy is higher
- Shoots when close (< 400 pixels)
- Aggressive when health > 50%

### FuzzyAI (Advanced)
Full fuzzy logic implementation using scikit-fuzzy.

```python
from fuzzy_ai import FuzzyAI

ai = FuzzyAI()  # Auto-falls back to SimpleFuzzyAI if scikit-fuzzy missing

actions = ai.decide_action(ai_state, enemy_state)
```

**Fuzzy Variables:**

| Input | Range | Membership Functions |
|-------|-------|---------------------|
| `distance` | 0-1000 | close, medium, far |
| `health` | 0-100 | low, medium, high |
| `enemy_health` | 0-100 | low, medium, high |
| `height_diff` | -500 to 500 | below, same, above |

| Output | Range | Membership Functions |
|--------|-------|---------------------|
| `aggression` | 0-100 | defensive, balanced, aggressive |
| `should_jump` | 0-100 | no, maybe, yes |

**Sample Rules:**
- IF health is low → THEN aggression is defensive
- IF health is high AND enemy_health is low → THEN aggression is aggressive
- IF distance is close AND health is high → THEN aggression is aggressive
- IF height_diff is below → THEN should_jump is yes
- IF health is low AND distance is close → THEN should_jump is yes

## Running the Game with AI

### Quick Start
```cmd
python play_vs_ai.py
```

### What Happens
1. Python initializes game window
2. Player 1: **Human** (keyboard: WASD + Space)
3. Player 2: **AI** (controlled by fuzzy logic)
4. Game runs at ~60 FPS
5. AI reads game state, decides actions, sends commands
6. Debug output shows AI decisions and player stats

### Expected Output
```
============================================================
GUN MAYHEM - Human vs Fuzzy AI
============================================================
Player 1: YOU (Controlled by keyboard in game)
Player 2: FUZZY AI (Controlled by Python)

Starting game...
Game running! Play with the keyboard, AI will control Player 2
AI taking control of player_1

[DEBUG] AI Actions: {'up': False, 'left': False, 'right': True, 'down': False, 'primaryFire': True, 'secondaryFire': False}

[Frame 60] Players: 2, Bullets: 3
  [HUMAN] player_0: HP=100.0, Lives=3, Pos=( 350.2,  420.5)
  [AI   ] player_1: HP= 85.0, Lives=3, Pos=( 680.1,  410.3)
```

## Troubleshooting

### AI Not Moving
**Symptom:** AI actions print correctly but player doesn't move.

**Causes & Solutions:**
1. **Keyboard override:** AI commands are being overwritten by keyboard input
   - **Fix:** Ensure `game_control.disable_keyboard_for_player()` is called
   - **Verify:** Check `src/PlayState.cpp` has the skip logic in `updatePlayerInputs()`
   
2. **Module out of date:** Changes to C++ code not reflected in `.pyd`
   - **Fix:** Clean rebuild
     ```cmd
     rmdir /s /q build_pybind
     build_python_module.bat
     ```

3. **Wrong player ID:** Controlling wrong player or typo in ID
   - **Fix:** Print `list(players.keys())` and verify IDs match

### Module Import Errors
```
ImportError: DLL load failed while importing gunmayhem
```

**Solution:** Add DLL directories before import
```python
import os
os.add_dll_directory(r"C:\MinGW\bin")  # Your MinGW path
os.add_dll_directory(r"C:\Users\...\Gun-Mayhem\libs\SDL2-2.32.8\x86_64-w64-mingw32\bin")

import gunmayhem  # Now this works
```

### NumPy Boolean Issues
```
TypeError: incompatible function arguments
```

**Cause:** PyBind11 doesn't auto-convert `np.True_` / `np.False_`

**Solution:** Wrap all boolean values
```python
game_control.set_player_movement(
    player_id,
    bool(ai_actions['up']),        # Convert to Python bool
    bool(ai_actions['left']),
    bool(ai_actions['down']),
    bool(ai_actions['right']),
    bool(ai_actions['primaryFire']),
    bool(ai_actions['secondaryFire'])
)
```

### Build Errors

**"Python.h not found"**
```
fatal error: Python.h: No such file or directory
```
**Solution:** Reinstall Python with dev headers, or use `py -m pip install pybind11`

**"PLATFORM macro redefinition"**
```
error: 'PLATFORM' was not declared in this scope
```
**Solution:** Already fixed in `src/python_bindings.cpp` with `#undef PLATFORM`

**"C++17 structured bindings"**
```
error: structured bindings only available with '-std=c++17'
```
**Solution:** Upgrade MinGW to GCC 13+ (CMakeLists.txt sets C++17 automatically)

### Game Crashes

**Segmentation fault on `update()`**
- **Cause:** Game not properly initialized
- **Solution:** Check `init_game()` returns `True` before entering loop

**"Failed to load texture"**
- **Cause:** Running from wrong directory (can't find `../assets/`)
- **Solution:** Script automatically changes to `build/` directory

## Advanced Usage

### Custom AI Implementation

```python
class MyCustomAI:
    def decide_action(self, ai_state, enemy_state):
        # Your logic here
        return {
            'up': ...,
            'left': ...,
            'right': ...,
            'down': ...,
            'primaryFire': ...,
            'secondaryFire': ...
        }

# Use in game loop
ai = MyCustomAI()
actions = ai.decide_action(player2_state, player1_state)
game_control.set_player_movement(
    'player_1',
    bool(actions['up']),
    bool(actions['left']),
    bool(actions['down']),
    bool(actions['right']),
    bool(actions['primaryFire']),
    bool(actions['secondaryFire'])
)
```

### Multiple AI Players

```python
ai1 = FuzzyAI()
ai2 = SimpleFuzzyAI()

players = game_state.get_all_players()
player_ids = list(players.keys())

# Disable keyboard for both
game_control.disable_keyboard_for_player(player_ids[0])
game_control.disable_keyboard_for_player(player_ids[1])

# Control both players
actions1 = ai1.decide_action(players[player_ids[0]], players[player_ids[1]])
actions2 = ai2.decide_action(players[player_ids[1]], players[player_ids[0]])

# Send commands
game_control.set_player_movement(player_ids[0], bool(actions1['up']), ...)
game_control.set_player_movement(player_ids[1], bool(actions2['up']), ...)
```

### Data Collection for ML

```python
import json

training_data = []

while game.is_running():
    game.handle_events()
    
    players = game_state.get_all_players()
    bullets = game_state.get_all_bullets()
    
    # Collect state
    frame_data = {
        'players': players,
        'bullets': bullets,
        'timestamp': time.time()
    }
    training_data.append(frame_data)
    
    game.update(0.0166)
    game.render()

# Save for training
with open('gameplay_data.json', 'w') as f:
    json.dump(training_data, f)
```

## File Structure

```
Gun-Mayhem/
├── src/
│   ├── python_bindings.cpp     # PyBind11 wrapper implementation
│   ├── PlayState.cpp            # Modified for AI control
│   └── ...                      # Other C++ sources
├── include/
│   ├── PlayState.hpp            # Added public getters
│   └── ...
├── build_pybind/                # Python module build directory
│   └── gunmayhem.*.pyd          # Compiled Python module
├── fuzzy_ai.py                  # Fuzzy logic AI (SimpleFuzzyAI, FuzzyAI)
├── play_vs_ai.py                # Main script (Human vs AI)
├── build_python_module.bat      # Build script
├── CMakeLists_pybind.txt        # CMake config for Python module
└── PYTHON_BINDINGS_README.md    # This file
```

## Next Steps

1. **Improve AI:** Tune fuzzy membership functions and rules
2. **Add Features:** Expose weapon switching, special abilities
3. **Machine Learning:** Train neural network using collected data
4. **Tournament Mode:** Create Python script to run AI vs AI tournaments
5. **Visualization:** Add Matplotlib plots of AI decision-making

## Resources

- [PyBind11 Documentation](https://pybind11.readthedocs.io/)
- [scikit-fuzzy Documentation](https://pythonhosted.org/scikit-fuzzy/)
- [SDL2 Documentation](https://wiki.libsdl.org/)

## Credits

- **Game Engine:** C++ with SDL2
- **Python Bindings:** PyBind11
- **AI Framework:** scikit-fuzzy
- **Fuzzy Logic:** Developed for intelligent player control
