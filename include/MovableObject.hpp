#pragma once

#include "GameObject.hpp"

class MovableObject : public GameObject {
public:
    enum FacingDirection {
        LEFT,
        RIGHT
    };

    MovableObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
                  float scale = 1, double rotation = 0);
                  
    void draw() override;

protected:
    Vector2D velocity;
    FacingDirection facingDirection;
};