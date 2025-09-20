#pragma once

#include "Vector2D.hpp"
#include <SDL.h>
#include <string>

class GameObject {
public:
    enum GameObjectType {
        PLAYER,
        PLATFORM,
        BULLET,
        WEAPON,
        UNKNOWN
    };

    GameObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
               float scale = 1, double rotation = 0);

    virtual void draw();
    virtual void update(float deltaTime);
    virtual void clean();

    virtual GameObjectType getGameObjectType() const { return GameObjectType::UNKNOWN; }
    std::string &getId() { return id; }
    SDL_FRect &getColliderRect() { return colliderRect; }

    virtual ~GameObject() {}
protected:

    std::string id;

    SDL_FRect colliderRect;
    SDL_FRect renderRect;

    float scale;
    double rotation;
};