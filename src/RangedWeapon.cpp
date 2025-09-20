#include "RangedWeapon.hpp"
#include <iostream>

RangedWeapon::RangedWeapon(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color,
                           float scale, double rotation)
    : Weapon(id, playerId, x, y, w, h, color, scale, rotation) {
        isReloading = false;
}

void RangedWeapon::fire(FireMode mode) {
    if (isReloading) {
        return;
    }

    if (mode == FireMode::PRIMARY) {
        if (ammo > 0 && timeSinceLastPrimaryFire >= primaryFireCooldown) {
            // std::cout << "prim" << std::endl;
            if (spawnBullet) {
                spawnBullet(playerId, mode);
            }
            ammo--;
            timeSinceLastPrimaryFire = 0;
            if (ammo == 0) {
                reload();
            }
        }
    } else if (mode == FireMode::SECONDARY) {
        if (ammo > 0 && timeSinceLastSecondaryFire >= secondaryFireCooldown) {
            // std::cout << "sec" << std::endl;
            if (spawnBullet) {
                spawnBullet(playerId, mode);
            }
            ammo--;
            timeSinceLastSecondaryFire = 0;
            if (ammo == 0) {
                reload();
            }
        }
    }
}

void RangedWeapon::update(float deltaTime) {
    Weapon::update(deltaTime);

    if (isReloading) {
        reloadTimer += deltaTime;
        if (reloadTimer >= reloadTime) {
            ammo = maxAmmo;
            isReloading = false;
            reloadTimer = 0.0f;
        }
    }
}

void RangedWeapon::reload() {
    if (!isReloading && ammo < maxAmmo) {
        isReloading = true;
        reloadTimer = 0.0f;
    }
}