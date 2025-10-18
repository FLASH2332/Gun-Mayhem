#include "PlayState.hpp"
#include "Bullet.hpp"
#include "CollisionHandler.hpp"
#include "GameObject.hpp"
#include "InputHandler.hpp"
#include "Platform.hpp"
#include "Player.hpp"
#include "RangedWeapon.hpp"
#include "TextureManager.hpp"
#include "Vector2D.hpp"
#include "Weapon.hpp"
#include "utils.hpp"
#include <algorithm>
#include <iostream>

bool PlayState::onEnter() {
    std::string gameConfigFileName = "../assets/gameConfig.json";

    utils::MapData mapData = utils::loadRandomMapFromJson(gameConfigFileName);
    if (mapData.platforms.empty()) {
        std::cout << "Map loading failed." << std::endl;
        return false;
    }
    for (auto &platform : mapData.platforms) {
        layeredGameObjectsMap["platforms"][platform->getId()] = std::move(platform);
    }
    for (const auto &[id, ptr] : layeredGameObjectsMap["platforms"]) {
        sortedPlatformsId.push_back(id);
    }
    std::sort(sortedPlatformsId.begin(), sortedPlatformsId.end(),
              [&](const std::string &a, const std::string &b) {
                  return layeredGameObjectsMap["platforms"][a]->getColliderRect().y <
                         layeredGameObjectsMap["platforms"][b]->getColliderRect().y;
              });

    utils::PlayerData playerData = utils::loadPlayersFromJson(gameConfigFileName, mapData.spawnPoints);
    if (playerData.players.empty()) {
        std::cout << "Player loading failed." << std::endl;
        return false;
    }
    for (auto &player : playerData.players) {
        std::string weaponType = "pistol";
        std::unique_ptr<Weapon> weapon = utils::createWeapon(
            weaponType,
            player->getId(),
            player->getColliderRect().x,
            player->getColliderRect().y);

        player->setPrimaryWeapon(weapon.get());

        auto playerId = player->getId();
        if (auto *rw = dynamic_cast<RangedWeapon *>(weapon.get())) {
            rw->setSpawnBulletCallback([this, playerId](const std::string &, Weapon::FireMode mode) {
                this->spawnBullet(playerId, mode);
            });
        }

        layeredGameObjectsMap["weapons"][weapon->getId()] = std::move(weapon);
        layeredGameObjectsMap["player"][player->getId()] = std::move(player);
    }

    playerControls = utils::loadPlayerControls(gameConfigFileName);

    layerOrder = {"platforms", "player", "weapons", "bullets"};

    std::cout << "entering PlayState..." << std::endl;
    return true;
}

void PlayState::spawnBullet(const std::string &playerId, Weapon::FireMode mode) {

    // std::cout << "bullet" << std::endl;
    auto &players = layeredGameObjectsMap["player"];
    auto it = players.find(playerId);
    if (it == players.end())
        return;

    Player *player = static_cast<Player *>(it->second.get());

    float bx = player->getColliderRect().x + player->getColliderRect().w / 2;
    float by = player->getColliderRect().y + player->getColliderRect().h / 2;
    Vector2D dir = (player->getFacingDirection() == MovableObject::LEFT) ? Vector2D(-1, 0) : Vector2D(1, 0);

    std::string bulletId = playerId + "_bullet_" + std::to_string(SDL_GetTicks());
    SDL_Color bulletColor = {255, 255, 0, 255};

    auto bullet = std::make_unique<Bullet>(bulletId, playerId, bx, by, 8, 4, bulletColor, dir, 1000.0f);
    layeredGameObjectsMap["bullets"][bulletId] = std::move(bullet);
}

bool PlayState::onExit() {
    for (auto &[layer, gameObjectsMap] : layeredGameObjectsMap) {
        for (auto &[id, gameObject] : gameObjectsMap) {
            gameObject->clean();
        }
    }
    layeredGameObjectsMap.clear();

    std::cout << "exiting PlayState..." << std::endl;
    return true;
}

void PlayState::update(float deltaTime) {
    updatePlayerInputs();
    updateGameObjects(deltaTime);
    handleCollisions();

    // TODO: remove from gameobjectmap if they move out of the screen or are destroyed
}

void PlayState::updatePlayerInputs() {
    for (auto &[id, gameObject] : layeredGameObjectsMap["player"]) {
        Player *player = dynamic_cast<Player *>(gameObject.get());
        if (player) {
            // Skip players that don't have keyboard controls (AI-controlled)
            if (playerControls.find(player->getId()) == playerControls.end()) {
                continue;
            }
            
            utils::PlayerControls &controls = playerControls[player->getId()];
            Player::MovementInput input;
            if (_InputHandler::Instance().isKeyDown(controls.left))
                input.left = true;
            if (_InputHandler::Instance().isKeyDown(controls.right))
                input.right = true;
            if (_InputHandler::Instance().isKeyDown(controls.up))
                input.up = true;
            if (_InputHandler::Instance().isKeyDown(controls.down))
                input.down = true;
            if (_InputHandler::Instance().isKeyDown(controls.primaryShoot))
                input.primaryFire = true;
            if (_InputHandler::Instance().isKeyDown(controls.secondaryShoot))
                input.secondaryFire = true;
            player->setMovement(input);
        }
    }
}

void PlayState::updateGameObjects(float deltaTime) {
    for (auto &[layer, gameObjectsMap] : layeredGameObjectsMap) {

        for (auto &[id, gameObject] : gameObjectsMap) {
            // std::cout << id << std::endl;
            gameObject->update(deltaTime);
        }
    }

    for (auto it = layeredGameObjectsMap["bullets"].begin(); it != layeredGameObjectsMap["bullets"].end();) {
        Bullet *b = static_cast<Bullet *>(it->second.get());
        if (b->isExpired()) {
            it = layeredGameObjectsMap["bullets"].erase(it);
        } else {
            ++it;
        }
    }
}

void PlayState::handleCollisions() {
    // player-platform collisions
    for (auto &[id, gameObject] : layeredGameObjectsMap["player"]) {
        Player *player = static_cast<Player *>(gameObject.get());
        auto it = std::lower_bound(sortedPlatformsId.begin(), sortedPlatformsId.end(), player->getColliderRect().y,
                                   [&](const std::string &id, int y) {
                                       const SDL_FRect &rect = layeredGameObjectsMap["platforms"][id]->getColliderRect();
                                       return rect.y + rect.h < y;
                                   });
        if (it == sortedPlatformsId.end())
            continue;

        int firstPlatformy = layeredGameObjectsMap["platforms"][*it]->getColliderRect().y;
        while (it != sortedPlatformsId.end() &&
               layeredGameObjectsMap["platforms"][*it]->getColliderRect().y == firstPlatformy) {
            const SDL_FRect &platRect = layeredGameObjectsMap["platforms"][*it]->getColliderRect();
            // std::cout << "Checking collision with platform: " << *it << std::endl;
            if (SDL_HasIntersectionF(&player->getColliderRect(), &platRect)) {
                player->onCollisionWithPlatform(platRect);
                break;
            }
            ++it;
        }
    }

    for (auto &[id, gameObject] : layeredGameObjectsMap["bullets"]) {
        Bullet *bullet = static_cast<Bullet *>(gameObject.get());
        for (auto &[pid, pgameObject] : layeredGameObjectsMap["player"]) {
            Player *player = static_cast<Player *>(pgameObject.get());
            if (bullet->getPlayerId() == player->getId())
                continue;
            if (SDL_HasIntersectionF(&bullet->getColliderRect(), &player->getColliderRect())) {
                MovableObject::FacingDirection facingDir =
                    (bullet->getDirection().x < 0) ? MovableObject::FacingDirection::LEFT : MovableObject::FacingDirection::RIGHT;
                player->onCollisionWithBullet(bullet->getDamage(), bullet->getKnockback(), facingDir);
                bullet->setExpired(true);
                break;
            }
        }
    }
}

void PlayState::render() {
    for (const std::string &layer : layerOrder) {
        for (auto &[id, gameObject] : layeredGameObjectsMap[layer]) {
            gameObject->draw();
        }
    }
}

void PlayState::onKeyDown(SDL_Event &event) {
}

void PlayState::onKeyUp(SDL_Event &event) {
}

void PlayState::onMouseButtonDown(SDL_Event &event) {
}

void PlayState::onMouseButtonUp(SDL_Event &event) {
}

void PlayState::onMouseMove(SDL_Event &event) {
}
