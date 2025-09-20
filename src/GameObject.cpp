#include "GameObject.hpp"
#include "Game.hpp"
#include "TextureManager.hpp"
#include <iostream>

GameObject::GameObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
                       float scale, double rotation)
    : id(id),
      scale(scale),
      rotation(rotation),
      colliderRect({x, y, w, h}),
      renderRect(colliderRect) {

    _TextureManager::Instance().createTextureFromRect(id, renderRect, color);
}

void GameObject::update(float deltaTime) {
}

void GameObject::draw() {
    _TextureManager::Instance().draw(id, renderRect, rotation);
}

void GameObject::clean() {
    _TextureManager::Instance().removeFromTextureMap(id);
}