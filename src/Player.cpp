#include "Player.hpp"
#include "Game.hpp"
#include "GameObject.hpp"
#include "TextureManager.hpp"
#include <cstdlib>
#include <iostream>
#include "RangedWeapon.hpp"

Player::Player(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
               float scale, double rotation)
    : MovableObject(id, x, y, w, h, color, scale, rotation),
      prevPos(x, y) {

    init();
    // giveWeapon();
}

void Player::init() {
    knockbackVelocity = {0, 0};
    jumpCount = 1;
    wasJumping = true;
    onGround = false;
    lives = maxLives;
    health = maxHealth;
    facingDirection = FacingDirection::LEFT;
}

void Player::setMovement(Player::MovementInput &movementInput) {
    this->movementInput = movementInput;
}

// void Player::draw() {
//     SDL_RendererFlip flip = (facingDirection == FacingDirection::LEFT) ? SDL_FLIP_HORIZONTAL : SDL_FLIP_NONE;
//     _TextureManager::Instance().draw(id, renderRect, rotation, flip);

//     std::string info = "HP: " + std::to_string((int)getHealth()) +
//                        " | Lives: " + std::to_string((int)getLives());
//     SDL_Surface *fontSurface = TTF_RenderText_Blended(_Game::Instance().getFont(), info.c_str(), {255, 255, 255, 255});
//     SDL_Texture *fontTexture = SDL_CreateTextureFromSurface(_Game::Instance().getRenderer(), fontSurface);

//     SDL_FRect dstRect = {colliderRect.x, colliderRect.y - 20, (float)fontSurface->w, (float)fontSurface->h};
//     SDL_RenderCopyF(Game::Instance().getRenderer(), fontTexture, nullptr, &dstRect);

//     SDL_FreeSurface(fontSurface);
//     SDL_DestroyTexture(fontTexture);
// }

void Player::draw() {
    SDL_RendererFlip flip = (facingDirection == FacingDirection::LEFT) ? SDL_FLIP_HORIZONTAL : SDL_FLIP_NONE;
    _TextureManager::Instance().draw(id, renderRect, rotation, flip);

    std::string weaponName = primaryWeapon ? primaryWeapon->getName() : "None";
    int ammo = primaryWeapon ? primaryWeapon->getAmmo() : 0;
    int maxAmmo = primaryWeapon ? primaryWeapon->getMaxAmmo() : 0;
    bool reloading = false;
    if (primaryWeapon) {
        if (auto rw = dynamic_cast<RangedWeapon*>(primaryWeapon)) {
            reloading = rw->getIsReloading();
        }
    }

    std::vector<std::string> lines = {
        "HP: " + std::to_string(health) + "/" + std::to_string(maxHealth),
        "Lives: " + std::to_string(lives) + "/" + std::to_string(maxLives),
        "Weapon: " + weaponName,
        "Ammo: " + std::to_string(ammo) + "/" + std::to_string(maxAmmo) + (reloading ? " (Reloading)" : "")
    };

    int lineHeight = 18; // or use TTF_FontLineSkip(font)
    int yOffset = -80;

    for (const auto& line : lines) {
        SDL_Surface* fontSurface = TTF_RenderText_Blended(_Game::Instance().getFont(), line.c_str(), {255, 255, 255, 255});
        SDL_Texture* fontTexture = SDL_CreateTextureFromSurface(_Game::Instance().getRenderer(), fontSurface);

        SDL_FRect dstRect = {colliderRect.x, colliderRect.y + yOffset, (float)fontSurface->w, (float)fontSurface->h};
        SDL_RenderCopyF(_Game::Instance().getRenderer(), fontTexture, nullptr, &dstRect);

        SDL_FreeSurface(fontSurface);
        SDL_DestroyTexture(fontTexture);

        yOffset += lineHeight;
    }
}

void Player::update(float deltaTime) {
    handleXMovement();

    handleJump();


    // TODO: this will make the player gravity weaker even if the player is releases and presses up button again
    // before reaching top of the jump; decide later if this can be a feature or should be removed
    applyGravity(deltaTime);

    if (colliderRect.y > 640 + 50) {
        respawn();
    }

    updatePosition(deltaTime);
    handleWeapon();
}

void Player::handleWeapon() {
    if (primaryWeapon) {
        primaryWeapon->setPlayerPosition(colliderRect.x, colliderRect.y);
        primaryWeapon->setPlayerFacingDirection(facingDirection);
    }
    if (secondaryWeapon) {
        secondaryWeapon->setPlayerPosition(colliderRect.x, colliderRect.y);
        secondaryWeapon->setPlayerFacingDirection(facingDirection);
    }

    if (movementInput.primaryFire) {
        if (secondaryWeapon) {
            secondaryWeapon->fire(Weapon::PRIMARY);
            // if (secondaryWeapon->isOutOfAmmo()) {
            //     secondaryWeapon = nullptr; // fallback to primary
            // }
        } else if (primaryWeapon) {
            primaryWeapon->fire(Weapon::PRIMARY);
        }
    }
    if (movementInput.secondaryFire) {
        if (secondaryWeapon) {
            secondaryWeapon->fire(Weapon::SECONDARY);
            // if (secondaryWeapon->isOutOfAmmo()) {
            //     secondaryWeapon = nullptr;
            // }
        } else if (primaryWeapon) {
            primaryWeapon->fire(Weapon::SECONDARY);
        }
    }
}

void Player::handleXMovement() {
    velocity.x = 0;
    if (movementInput.left) {
        velocity.x = -xSpeed;
        facingDirection = FacingDirection::LEFT;
    }
    if (movementInput.right) {
        velocity.x = xSpeed;
        facingDirection = FacingDirection::RIGHT;
    }
}

void Player::handleJump() {
    if (movementInput.up && !wasJumping && jumpCount < maxJumps) {
        velocity.y = -jumpSpeed;
        jumpCount++;
    }
    wasJumping = movementInput.up;
}

void Player::applyGravity(float deltaTime) {
    if (!movementInput.up && velocity.y < 0) {
        velocity.y += strongGravity * deltaTime;
    } else {
        velocity.y += gravity * deltaTime;
    }

    if (velocity.y > maxFallSpeed) {
        velocity.y = maxFallSpeed;
    }
}

void Player::updatePosition(float deltaTime) {
    prevPos = {colliderRect.x, colliderRect.y};

    colliderRect.x += (velocity.x + knockbackVelocity.x) * deltaTime;
    colliderRect.y += (velocity.y + knockbackVelocity.y) * deltaTime;

    renderRect.x = colliderRect.x;
    renderRect.y = colliderRect.y;

    if (onGround && velocity.y > 0) {
        onGround = false;
        jumpCount = 1;
    }

    knockbackVelocity *= 0.9f; // decay knockback over time
    if (std::abs(knockbackVelocity.x) < 0.01f)
        knockbackVelocity.x = 0;
    if (std::abs(knockbackVelocity.y) < 0.01f)
        knockbackVelocity.y = 0;
}

void Player::setPrimaryWeapon(Weapon *pw) {
    // if (weapon) {
    //     weapon->clean();
    //     delete weapon;
    // }
    primaryWeapon = pw;
}

void Player::respawn() {
    // TODO: update this with screen size
    if (--lives > 0) {
        colliderRect.x = 480;
        colliderRect.y = -50;
        renderRect.x = colliderRect.x;
        renderRect.y = colliderRect.y;

        velocity = {0, 0};
        jumpCount = 1;
        health = maxHealth;

        // weapon->reset();
    }
}

// void Player::clean() {
//     GameObject::clean();

//     if (weapon) {
//         weapon->clean();
//         delete weapon;
//         weapon = nullptr;
//     }
// }

void Player::onCollisionWithPlatform(const SDL_FRect &platformColliderRect) {
    if (movementInput.down) {
        jumpCount = 1;
        return;
    }

    float feetY = colliderRect.y + colliderRect.h;
    float prevFeetY = prevPos.y + colliderRect.h;
    bool isFalling = velocity.y >= 0;
    bool isAbove = prevFeetY <= platformColliderRect.y;

    if (isAbove && isFalling) {
        colliderRect.y = platformColliderRect.y - colliderRect.h;
        velocity.y = 0;
        jumpCount = 0;
        onGround = true;
    }
}

void Player::onCollisionWithBullet(float damage, float knockback, FacingDirection bulletFacingDirection){
    health -= damage;
    if (health <= 0) {
        if (lives > 0) {
            respawn();
        }
    }
    // Consistent knockback direction
    float direction = (bulletFacingDirection == FacingDirection::RIGHT) ? 1.0f : -1.0f;
    knockbackVelocity.x = direction * knockback;
    knockbackVelocity.y = -1.0f * knockback; // Upward knockback
}