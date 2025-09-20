#pragma once

#include "MovableObject.hpp"
#include "Vector2D.hpp"
#include <string>

class Bullet : public MovableObject {
public:
    Bullet(const std::string& id,
           const std::string& ownerId,
           float x, float y,
           float w, float h,
           const SDL_Color& color,
           const Vector2D& dir,
           float speed); // seconds until bullet auto-despawns

    GameObjectType getGameObjectType() const override { return GameObjectType::BULLET; }

    void update(float deltaTime) override;

    const std::string& getPlayerId() const { return ownerId; }
    const Vector2D& getDirection() const { return direction; }
    int getDamage() const { return 10; }
    float getKnockback() const { return 500.0f; }
    void setExpired(bool exp) { expired = exp; }

    bool isExpired() const { return expired; }

private:
    std::string ownerId;   
    Vector2D direction;    
    float speed;           
    bool expired;
};
