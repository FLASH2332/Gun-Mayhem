#pragma once

#include "MovableObject.hpp"
#include "Vector2D.hpp"

class Weapon : public MovableObject {
public:
    enum FireMode {
        PRIMARY,
        SECONDARY
    };

    Weapon(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color, float scale = 1, double rotation = 0);

    void update(float deltaTime) override;
    virtual std::string getName() const = 0;

    virtual void fire(FireMode mode) = 0;
    void reload();

    void setPlayerPosition(float x, float y);
    void setPlayerFacingDirection(FacingDirection dir) { playerFacingDirection = dir; }

    int getAmmo() const { return ammo; }
    int getMaxAmmo() const { return maxAmmo; }

protected:
    std::string playerId;
    int ammo;
    int maxAmmo;
    float primaryFireCooldown;
    float timeSinceLastPrimaryFire;
    float secondaryFireCooldown;
    float timeSinceLastSecondaryFire;

    bool isPrimaryWeapon;

    Vector2D playerPosition;
    FacingDirection playerFacingDirection;
};