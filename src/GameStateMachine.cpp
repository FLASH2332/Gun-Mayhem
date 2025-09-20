#include "GameStateMachine.hpp"
#include <iostream>

void GameStateMachine::pushState(GameState *state) {
    gameStates.push_back(state);
    gameStates.back()->onEnter();
}

void GameStateMachine::changeState(GameState *state) {
    if (!gameStates.empty()) {
        if (gameStates.back()->getStateId() == state->getStateId()) {
            return;
        }
    }

    gameStates.push_back(state);

    if (!gameStates.empty()) {
        if (gameStates.back()->onExit()) {
            gameStates.erase(gameStates.end() - 2);
        }
    }

    gameStates.back()->onEnter();
}

void GameStateMachine::popState() {
    if (!gameStates.empty()) {
        if (gameStates.back()->onExit()) {
            gameStates.erase(gameStates.end() - 1);
        }
    }
}

void GameStateMachine::update(float deltaTime) {
    if (!gameStates.empty()) {
        gameStates.back()->update(deltaTime);
    }
}

void GameStateMachine::render() {
    if (!gameStates.empty()) {
        gameStates.back()->render();
    }
}

void GameStateMachine::onKeyDown(SDL_Event &event) {
    if (!gameStates.empty()) {
        gameStates.back()->onKeyDown(event);
    }
}

void GameStateMachine::onKeyUp(SDL_Event &event) {
    if (!gameStates.empty()) {
        gameStates.back()->onKeyUp(event);
    }
}

void GameStateMachine::onMouseButtonDown(SDL_Event &event) {
    if (!gameStates.empty()) {
        gameStates.back()->onMouseButtonDown(event);
    }
}

void GameStateMachine::onMouseButtonUp(SDL_Event &event) {
    if (!gameStates.empty()) {
        gameStates.back()->onMouseButtonUp(event);
    }
}

void GameStateMachine::onMouseMove(SDL_Event &event) {
    if (!gameStates.empty()) {
        gameStates.back()->onMouseMove(event);
    }
}