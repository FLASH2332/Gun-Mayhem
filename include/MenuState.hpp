#pragma once

#include "Game.hpp"
#include "GameState.hpp"
#include "GameStateMachine.hpp"
#include <SDL.h>
#include <iostream>
#include <string>

class MenuState : public GameState {
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

    virtual const std::string getStateId() { return "MENU"; }

private:
};