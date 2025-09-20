#pragma once

#include "NonMovableObject.hpp"
#include <SDL.h>

class Platform : public NonMovableObject {
public:
    Platform(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
             float scale = 1, double rotation = 0);

    GameObjectType getGameObjectType() const { return GameObjectType::PLATFORM; }

private:
};