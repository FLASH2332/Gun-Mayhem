#include "Weapon.hpp"
#include <iostream>

Weapon::Weapon(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color,
               float scale, double rotation)
    : MovableObject(id, x, y, w, h, color, scale, rotation),
      playerId(playerId) {
}

void Weapon::reload() {
    ammo = maxAmmo;
}

void Weapon::update(float deltaTime) {
    if (timeSinceLastPrimaryFire < primaryFireCooldown) {
        timeSinceLastPrimaryFire += deltaTime;
    }
    if (timeSinceLastSecondaryFire < secondaryFireCooldown) {
        timeSinceLastSecondaryFire += deltaTime;
    }

    float weaponOffset = 10.0f; // how far away from the body
    if (playerFacingDirection == FacingDirection::LEFT) {
        colliderRect.x = playerPosition.x - colliderRect.w;
    } else {
        colliderRect.x = playerPosition.x + weaponOffset;
    }
    renderRect.x = colliderRect.x;

    // align vertically to player's center
    colliderRect.y = playerPosition.y + (colliderRect.h / 2);
    renderRect.y = colliderRect.y;
}

void Weapon::setPlayerPosition(float x, float y) {
    playerPosition = {x, y};
}