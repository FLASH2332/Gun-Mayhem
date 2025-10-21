#pragma once

#include "Game.hpp"
#include "GameState.hpp"
#include "GameStateMachine.hpp"
#include "utils.hpp"
#include <SDL.h>
#include <iostream>
#include <string>

class PlayState : public GameState {
public:
    virtual void update(float deltaTime);
    virtual void render();

    virtual bool onEnter();
    virtual bool onExit();

    virtual void onKeyDown(SDL_Event &event);
    virtual void onKeyUp(SDL_Event &event);
    virtual void onMouseButtonUp(SDL_Event &event);
    virtual void onMouseButtonDown(SDL_Event &event);
    virtual void onMouseMove(SDL_Event &event);

    virtual const std::string getStateId() { return "PLAY"; }

    // Public getters for Python bindings
    const auto& getLayeredGameObjectsMap() const { return layeredGameObjectsMap; }
    const auto& getPlayerControls() const { return playerControls; }
    auto& getPlayerControlsMutable() { return playerControls; }
    
    // Disable keyboard input for AI-controlled players
    void disableKeyboardForPlayer(const std::string& playerId) {
        playerControls.erase(playerId);
    }

private:
    std::unordered_map<std::string, utils::PlayerControls> playerControls;
    std::vector<std::string> sortedPlatformsId;

    void updatePlayerInputs();
    void updateGameObjects(float deltaTime);
    void handleCollisions();
    void spawnBullet(const std::string &playerId, Weapon::FireMode mode);
};