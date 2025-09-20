#include "CollisionHandler.hpp"
#include "GameObject.hpp"
#include "Platform.hpp"
#include "Player.hpp"
#include <iostream>

// void CollisionHandler::checkCollisions(GameObjectMap &gameObjectsMap) {
//     for (auto &gameObjectPair : gameObjectsMap) {
//         if (gameObjectPair.second->getObjectType() == GameObjectType::PLAYER) {
//             Player *player = dynamic_cast<Player *>(gameObjectPair.second);

//             for (auto &gameObjectPair2 : gameObjectsMap) {
//                 if (gameObjectPair2.second->getObjectType() == GameObjectType::PLATFORM) {
//                     GameObject *platform = gameObjectPair2.second;

//                     // TODO: replace this with raycast; update: raycast doesnt help much its the same logic again.
//                     // platforms collider can just be a horizontal line
//                     if (SDL_HasIntersectionF(&player->getColliderRectRef(), &platform->getColliderRectRef())) {
//                         if (player->onCollisionWithPlatform(platform->getColliderRectRef())) {
//                             break;
//                         }
//                     }
//                 }

//                 // if (gameObjectPair2.second->getObjectType() == GameObjectType::BULLET) {
//                 //     Bullet *bullet = dynamic_cast<Bullet *>(gameObjectPair2.second);
//                 //     if (player->getId() != bullet->getPlayerId()) {
//                 //         if (SDL_HasIntersectionF(&player->getColliderRectRef(), &bullet->getColliderRectRef())) {
//                 //             player->onCollisionWithBullet(bullet->getDamage(), bullet->getKnockback(), bullet->getFacingDirection());
//                 //         }
//                 //     }
//                 // }
//             }
//         }
//     }
// }