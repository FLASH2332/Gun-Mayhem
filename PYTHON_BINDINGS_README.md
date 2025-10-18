# Gun Mayhem - Python Bindings Setup

## Overview
This project now includes Python bindings using PyBind11, allowing you to:
- Read game state (player positions, health, bullets, etc.)
- Control players from Python
- Implement AI using scikit-fuzzy or other Python libraries

## Prerequisites

### C++ Build Tools
- **MinGW-w64** with GCC 13+ (already installed)
- **CMake** 3.15+
- **SDL2** libraries (included in `libs/`)

### Python Requirements
```bash
pip install pybind11 scikit-fuzzy numpy
```

## Building the Python Module

### Option 1: Using the build script
```cmd
build_python_module.bat
```

### Option 2: Manual build
```cmd
mkdir build_pybind
cd build_pybind
cmake .. -G "MinGW Makefiles" -f ../CMakeLists_pybind.txt
mingw32-make
```

This will create `gunmayhem.pyd` (the Python module).

## Using the Python Bindings

### 1. Import the module
```python
import gunmayhem

# Create wrappers
game_state = gunmayhem.GameState()
game_control = gunmayhem.GameControl()
```

### 2. Read game state
```python
# Get all players
players = game_state.get_all_players()
for player_id, player_data in players.items():
    print(f"Player {player_id}:")
    print(f"  Position: ({player_data['x']}, {player_data['y']})")
    print(f"  Health: {player_data['health']}")
    print(f"  Lives: {player_data['lives']}")
    print(f"  Velocity: ({player_data['velocity_x']}, {player_data['velocity_y']})")

# Get all bullets
bullets = game_state.get_all_bullets()
for bullet_id, bullet_data in bullets.items():
    print(f"Bullet {bullet_id} from {bullet_data['owner_id']}")

# Get all platforms
platforms = game_state.get_all_platforms()

# Get game info
info = game_state.get_game_info()
print(f"Screen: {info['screen_width']}x{info['screen_height']}")
```

### 3. Control players
```python
# Control a player
game_control.set_player_movement(
    player_id="player1",
    up=True,      # Jump
    left=False,   # Move left
    down=False,   # Move down
    right=True,   # Move right
    primaryFire=True,    # Shoot
    secondaryFire=False  # Alt fire
)
```

### 4. Use with scikit-fuzzy
See `fuzzy_ai_example.py` for a complete example of using fuzzy logic to control the game.

## Exposed Data Structures

### Player State
- `id`: Player ID (string)
- `health`: Current health (0-100)
- `lives`: Remaining lives
- `x`, `y`: Position
- `velocity_x`, `velocity_y`: Velocity
- `width`, `height`: Dimensions
- `facing_direction`: 0=LEFT, 1=RIGHT
- `collider_x`, `collider_y`, `collider_w`, `collider_h`: Collision box

### Bullet State
- `id`: Bullet ID
- `owner_id`: Player who shot it
- `x`, `y`: Position
- `velocity_x`, `velocity_y`: Velocity
- `direction_x`, `direction_y`: Direction vector
- `damage`: Damage value
- `knockback`: Knockback force
- `expired`: Is bullet expired

### Platform State
- `id`: Platform ID
- `x`, `y`: Position
- `width`, `height`: Dimensions
- `collider_x`, `collider_y`, `collider_w`, `collider_h`: Collision box

## Example: Fuzzy Logic AI

```python
from fuzzy_ai_example import FuzzyGameAI

ai = FuzzyGameAI()

# In game loop
player_state = players['player1']
enemy_state = players['player2']

actions = ai.decide_action(player_state, enemy_state)
# Returns: {'move_left': bool, 'move_right': bool, 'jump': bool, 'shoot': bool, 'secondary_fire': bool}

game_control.set_player_movement(
    'player2',
    up=actions['jump'],
    left=actions['move_left'],
    right=actions['move_right'],
    down=False,
    primaryFire=actions['shoot'],
    secondaryFire=actions['secondary_fire']
)
```

## Integration Workflow

1. **Run the C++ game** (creates game instance)
2. **Run Python script** that imports `gunmayhem` module
3. **Python reads game state** every frame
4. **Python runs fuzzy logic** (or other AI)
5. **Python sends controls** back to game
6. **Game updates** based on Python inputs

## Troubleshooting

### Module not found
Make sure `gunmayhem.pyd` is in the same directory as your Python script, or add it to `PYTHONPATH`.

### DLL errors
Ensure `SDL2.dll` and `SDL2_ttf.dll` are in the same directory as the `.pyd` file.

### Build errors
- Verify GCC 13+ is installed: `gcc --version`
- Ensure Python development headers are installed
- Check that pybind11 is installed: `pip install pybind11`

## Next Steps

- Modify `fuzzy_ai_example.py` to match your fuzzy logic implementation
- Add more exposed functions in `python_bindings.cpp` as needed
- Create training loops for machine learning
- Implement tournament systems with Python-controlled players
