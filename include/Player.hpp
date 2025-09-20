#pragma once

#include "MovableObject.hpp"
#include "Vector2D.hpp"
#include "Weapon.hpp"
#include <SDL.h>

class Player : public MovableObject {
public:
    struct MovementInput {
        bool up = false;
        bool left = false;
        bool down = false;
        bool right = false;
        bool primaryFire = false;
        bool secondaryFire = false;
    };

    Player(const std::string &id, float x, float y, float w, float h, const SDL_Color &color, float scale = 1, double rotation = 0);
    void init();

    GameObjectType getGameObjectType() const { return GameObjectType::PLAYER; }
    void setMovement(Player::MovementInput &movInput);

    void draw() override;
    void update(float deltaTime) override;

    // bool onCollisionWithPlatform(SDL_FRect &platformColliderRect);
    // void onCollisionWithBullet(float damage, float knockback, FacingDirection bulletFacingDirection);
    // void clean();

    // Weapon *getWeapon() { return weapon; }
    void setPrimaryWeapon(Weapon *pw);
    void handleWeapon();
    float getHealth() { return health; }
    float getLives() { return lives; }
    FacingDirection getFacingDirection() const { return facingDirection; }

    void respawn();

    void onCollisionWithPlatform(const SDL_FRect &platformColliderRect);
    void onCollisionWithBullet(float damage, float knockback, FacingDirection bulletFacingDirection);

private:
    void handleXMovement();
    void handleJump();
    void applyGravity(float deltaTime);
    void updatePosition(float deltaTime);

    Player::MovementInput movementInput;

    Vector2D knockbackVelocity;

    float gravity = 2500;
    float strongGravity = 7500; // for smaller jumps when not holding up
    float maxFallSpeed = 1000;

    float jumpSpeed = 800;
    int jumpCount;
    int maxJumps = 2;
    bool wasJumping; // prev movementInput.up
    Vector2D prevPos;
    bool onGround;

    float xSpeed = 300;
    FacingDirection facingDirection;

    int lives;
    int maxLives = 10;
    int health;
    int maxHealth = 100;

    Weapon *primaryWeapon = nullptr;
    Weapon *secondaryWeapon = nullptr;
};