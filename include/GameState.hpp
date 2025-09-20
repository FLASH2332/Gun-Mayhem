#pragma once

#include "GameObject.hpp"
#include <SDL.h>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

class GameState {
public:
    virtual void update(float deltaTime) = 0;
    virtual void render() = 0;

    virtual bool onEnter() = 0;
    virtual bool onExit() = 0;

    virtual void onKeyDown(SDL_Event &event) = 0;
    virtual void onKeyUp(SDL_Event &event) = 0;
    virtual void onMouseButtonUp(SDL_Event &event) = 0;
    virtual void onMouseButtonDown(SDL_Event &event) = 0;
    virtual void onMouseMove(SDL_Event &event) = 0;

    virtual const std::string getStateId() = 0;

protected:
    std::unordered_map<std::string, std::unordered_map<std::string, std::unique_ptr<GameObject>>> layeredGameObjectsMap;
    std::vector<std::string> layerOrder;
};
