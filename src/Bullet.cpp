#include "Bullet.hpp"
#include <iostream>

Bullet::Bullet(const std::string &id,
               const std::string &ownerId,
               float x, float y,
               float w, float h,
               const SDL_Color &color,
               const Vector2D &dir,
               float speed)
    : MovableObject(id, x, y, w, h, color),
      ownerId(ownerId),
      direction(dir),
      speed(speed),
      expired(false) {
    // initial velocity = direction * speed
    direction.normalise();
    velocity = {direction.x * speed, direction.y * speed};
}

void Bullet::update(float deltaTime) {
    // move bullet
    colliderRect.x += velocity.x * deltaTime;
    colliderRect.y += velocity.y * deltaTime;
    renderRect.x = colliderRect.x;
    renderRect.y = colliderRect.y;

    // track age
    // age += deltaTime;
    // if (age >= lifetime) {
    //     expired = true;
    // }

    // (optional) check if bullet leaves screen bounds
    if (colliderRect.x < -50 || colliderRect.x > 1280 + 50 ||
        colliderRect.y < -50 || colliderRect.y > 720 + 50) {
        expired = true;
    }
}
