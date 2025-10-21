#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

// Undefine Windows/Python macros that conflict with our enums
#ifdef PLATFORM
#undef PLATFORM
#endif

#include "Game.hpp"
#include "Player.hpp"
#include "GameObject.hpp"
#include "Vector2D.hpp"
#include "PlayState.hpp"
#include "GameState.hpp"
#include "Bullet.hpp"
#include "Platform.hpp"
#include "MovableObject.hpp"

namespace py = pybind11;

// Helper functions to extract game state data
py::dict getPlayerState(Player* player) {
    if (!player) return py::dict();
    
    py::dict state;
    state["id"] = player->getId();
    state["health"] = player->getHealth();
    state["lives"] = player->getLives();
    
    // Access position through colliderRect
    auto rect = player->getColliderRect();
    state["x"] = rect.x;
    state["y"] = rect.y;
    state["width"] = rect.w;
    state["height"] = rect.h;
    
    // Velocity is protected - we'll need to add getters or leave it out for now
    state["velocity_x"] = 0.0f; // TODO: Add getter in MovableObject class
    state["velocity_y"] = 0.0f; // TODO: Add getter in MovableObject class
    
    state["facing_direction"] = static_cast<int>(player->getFacingDirection());
    
    state["collider_x"] = rect.x;
    state["collider_y"] = rect.y;
    state["collider_w"] = rect.w;
    state["collider_h"] = rect.h;
    
    return state;
}

py::dict getBulletState(Bullet* bullet) {
    if (!bullet) return py::dict();
    
    py::dict state;
    state["id"] = bullet->getId();
    state["owner_id"] = bullet->getPlayerId();
    
    auto rect = bullet->getColliderRect();
    state["x"] = rect.x;
    state["y"] = rect.y;
    
    // Velocity is protected
    state["velocity_x"] = 0.0f; // TODO: Add getter
    state["velocity_y"] = 0.0f; // TODO: Add getter
    
    auto dir = bullet->getDirection();
    state["direction_x"] = dir.x;
    state["direction_y"] = dir.y;
    
    state["damage"] = bullet->getDamage();
    state["knockback"] = bullet->getKnockback();
    state["expired"] = bullet->isExpired();
    
    return state;
}

py::dict getPlatformState(Platform* platform) {
    if (!platform) return py::dict();
    
    py::dict state;
    state["id"] = platform->getId();
    
    auto rect = platform->getColliderRect();
    state["x"] = rect.x;
    state["y"] = rect.y;
    state["width"] = rect.w;
    state["height"] = rect.h;
    
    state["collider_x"] = rect.x;
    state["collider_y"] = rect.y;
    state["collider_w"] = rect.w;
    state["collider_h"] = rect.h;
    
    return state;
}

// Wrapper class to expose game state
class GameStateWrapper {
public:
    py::dict getAllPlayers() {
        py::dict players;
        auto& gsm = _Game::Instance().getGameStateMachine();
        
        // Get the current state from the stack
        auto& states = gsm.getGameStates();
        if (states.empty()) return players;
        
        auto* currentState = dynamic_cast<PlayState*>(states.back());
        
        if (currentState) {
            const auto& objectsMap = currentState->getLayeredGameObjectsMap();
            auto it = objectsMap.find("player");
            if (it != objectsMap.end()) {
                for (const auto& [id, obj] : it->second) {
                    if (auto* player = dynamic_cast<Player*>(obj.get())) {
                        players[id.c_str()] = getPlayerState(player);
                    }
                }
            }
        }
        
        return players;
    }
    
    py::dict getAllBullets() {
        py::dict bullets;
        auto& gsm = _Game::Instance().getGameStateMachine();
        auto& states = gsm.getGameStates();
        if (states.empty()) return bullets;
        
        auto* currentState = dynamic_cast<PlayState*>(states.back());
        
        if (currentState) {
            const auto& objectsMap = currentState->getLayeredGameObjectsMap();
            auto it = objectsMap.find("bullets");
            if (it != objectsMap.end()) {
                for (const auto& [id, obj] : it->second) {
                    if (auto* bullet = dynamic_cast<Bullet*>(obj.get())) {
                        bullets[id.c_str()] = getBulletState(bullet);
                    }
                }
            }
        }
        
        return bullets;
    }
    
    py::dict getAllPlatforms() {
        py::dict platforms;
        auto& gsm = _Game::Instance().getGameStateMachine();
        auto& states = gsm.getGameStates();
        if (states.empty()) return platforms;
        
        auto* currentState = dynamic_cast<PlayState*>(states.back());
        
        if (currentState) {
            const auto& objectsMap = currentState->getLayeredGameObjectsMap();
            auto it = objectsMap.find("platforms");
            if (it != objectsMap.end()) {
                for (const auto& [id, obj] : it->second) {
                    if (auto* platform = dynamic_cast<Platform*>(obj.get())) {
                        platforms[id.c_str()] = getPlatformState(platform);
                    }
                }
            }
        }
        
        return platforms;
    }
    
    py::dict getGameInfo() {
        py::dict info;
        auto screenSize = _Game::Instance().getScreenSize();
        info["screen_width"] = screenSize.width;
        info["screen_height"] = screenSize.height;
        info["is_running"] = _Game::Instance().isRunning();
        return info;
    }
};

// Control wrapper to send commands to game
class GameControlWrapper {
public:
    void disableKeyboardForPlayer(const std::string& playerId) {
        auto& gsm = _Game::Instance().getGameStateMachine();
        auto& states = gsm.getGameStates();
        if (states.empty()) return;
        
        auto* currentState = dynamic_cast<PlayState*>(states.back());
        if (currentState) {
            currentState->disableKeyboardForPlayer(playerId);
        }
    }
    
    void setPlayerMovement(const std::string& playerId, 
                          bool up, bool left, bool down, bool right,
                          bool primaryFire, bool secondaryFire) {
        auto& gsm = _Game::Instance().getGameStateMachine();
        auto& states = gsm.getGameStates();
        if (states.empty()) return;
        
        auto* currentState = dynamic_cast<PlayState*>(states.back());
        
        if (currentState) {
            const auto& objectsMap = currentState->getLayeredGameObjectsMap();
            auto it = objectsMap.find("player");
            if (it != objectsMap.end()) {
                auto playerIt = it->second.find(playerId);
                if (playerIt != it->second.end()) {
                    if (auto* player = dynamic_cast<Player*>(playerIt->second.get())) {
                        Player::MovementInput input;
                        input.up = up;
                        input.left = left;
                        input.down = down;
                        input.right = right;
                        input.primaryFire = primaryFire;
                        input.secondaryFire = secondaryFire;
                        player->setMovement(input);
                    }
                }
            }
        }
    }
    
    void quitGame() {
        _Game::Instance().quit();
    }
};

// Game initialization and control
class GameRunner {
public:
    bool initGame(const std::string& title = "Gun Mayhem", 
                  int x = 100, int y = 100, int flags = 0x00000004) { // SDL_WINDOW_RESIZABLE = 0x00000004
        return _Game::Instance().init(title, x, y, flags);
    }
    
    void handleEvents() {
        _Game::Instance().handleEvents();
    }
    
    void update(float deltaTime) {
        _Game::Instance().update(deltaTime);
    }
    
    void render() {
        _Game::Instance().render();
    }
    
    bool isRunning() {
        return _Game::Instance().isRunning();
    }
    
    void quit() {
        _Game::Instance().quit();
    }
};

PYBIND11_MODULE(gunmayhem, m) {
    m.doc() = "Gun Mayhem Python Bindings";
    
    // Expose Vector2D
    py::class_<Vector2D>(m, "Vector2D")
        .def(py::init<float, float>())
        .def_readwrite("x", &Vector2D::x)
        .def_readwrite("y", &Vector2D::y)
        .def("length", &Vector2D::length);
    
    // Expose FacingDirection enum
    py::enum_<MovableObject::FacingDirection>(m, "FacingDirection")
        .value("LEFT", MovableObject::FacingDirection::LEFT)
        .value("RIGHT", MovableObject::FacingDirection::RIGHT);
    
    // Expose GameObjectType enum (avoiding PLATFORM macro conflict)
    py::enum_<GameObject::GameObjectType>(m, "GameObjectType")
        .value("PLAYER", GameObject::GameObjectType::PLAYER)
        .value("BULLET", GameObject::GameObjectType::BULLET)
        .value("PLATFORM", GameObject::GameObjectType::PLATFORM)
        .value("WEAPON", GameObject::GameObjectType::WEAPON)
        .value("UNKNOWN", GameObject::GameObjectType::UNKNOWN);
    
    // Expose Player::MovementInput
    py::class_<Player::MovementInput>(m, "MovementInput")
        .def(py::init<>())
        .def_readwrite("up", &Player::MovementInput::up)
        .def_readwrite("left", &Player::MovementInput::left)
        .def_readwrite("down", &Player::MovementInput::down)
        .def_readwrite("right", &Player::MovementInput::right)
        .def_readwrite("primaryFire", &Player::MovementInput::primaryFire)
        .def_readwrite("secondaryFire", &Player::MovementInput::secondaryFire);
    
    // Expose GameStateWrapper
    py::class_<GameStateWrapper>(m, "GameState")
        .def(py::init<>())
        .def("get_all_players", &GameStateWrapper::getAllPlayers)
        .def("get_all_bullets", &GameStateWrapper::getAllBullets)
        .def("get_all_platforms", &GameStateWrapper::getAllPlatforms)
        .def("get_game_info", &GameStateWrapper::getGameInfo);
    
    // Expose GameControlWrapper
    py::class_<GameControlWrapper>(m, "GameControl")
        .def(py::init<>())
        .def("disable_keyboard_for_player", &GameControlWrapper::disableKeyboardForPlayer)
        .def("set_player_movement", &GameControlWrapper::setPlayerMovement)
        .def("quit_game", &GameControlWrapper::quitGame);
    
    // Expose GameRunner - allows Python to control the game loop
    py::class_<GameRunner>(m, "GameRunner")
        .def(py::init<>())
        .def("init_game", &GameRunner::initGame, 
             py::arg("title") = "Gun Mayhem",
             py::arg("x") = 100,
             py::arg("y") = 100,
             py::arg("flags") = 0x00000004)
        .def("handle_events", &GameRunner::handleEvents)
        .def("update", &GameRunner::update)
        .def("render", &GameRunner::render)
        .def("is_running", &GameRunner::isRunning)
        .def("quit", &GameRunner::quit);
    
    // Helper functions
    m.def("get_player_state", &getPlayerState, "Get player state as dictionary");
    m.def("get_bullet_state", &getBulletState, "Get bullet state as dictionary");
    m.def("get_platform_state", &getPlatformState, "Get platform state as dictionary");
}
