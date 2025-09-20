#pragma once

#include "Weapon.hpp"
#include <functional>

class RangedWeapon : public Weapon {
public:
    RangedWeapon(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color, float scale = 1, double rotation = 0);
    void fire(FireMode mode) override;
    void update(float deltaTime) override;

    using SpawnBulletFn = std::function<void(const std::string &playerId, FireMode)>;
    void setSpawnBulletCallback(SpawnBulletFn cb) { spawnBullet = cb; }

    void reload();
    
    bool getIsReloading() const { return isReloading; }

protected:
    SpawnBulletFn spawnBullet;

    bool isReloading;
    float reloadTime;
    float reloadTimer;
};