#include "Pistol.hpp"

Pistol::Pistol(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color,
               float scale, double rotation)
    : RangedWeapon(id, playerId, x, y, w, h, color, scale, rotation) {
    maxAmmo = 12;
    ammo = maxAmmo;
    primaryFireCooldown = 0.2f;
    timeSinceLastPrimaryFire = primaryFireCooldown;
    secondaryFireCooldown = 0.5f;
    timeSinceLastSecondaryFire = secondaryFireCooldown;
    isPrimaryWeapon = true;
    reloadTime = 1.5f;
    reloadTimer = 0.0f;
}