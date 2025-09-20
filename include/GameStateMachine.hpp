#pragma once

#include "GameState.hpp"
#include <vector>
#include <SDL.h>

class GameStateMachine {
public:
    GameStateMachine() {}
    ~GameStateMachine() {}

    void pushState(GameState *state);
    void changeState(GameState *state);
    void popState();

    void update(float deltaTime);
    void render();

    void onKeyDown(SDL_Event &event);
    void onKeyUp(SDL_Event &event);
    void onMouseButtonUp(SDL_Event &event);
    void onMouseButtonDown(SDL_Event &event);
    void onMouseMove(SDL_Event &event);

    std::vector<GameState *> &getGameStates() { return gameStates; }

private:
    std::vector<GameState *> gameStates;
};