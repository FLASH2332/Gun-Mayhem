#include "MovableObject.hpp"
#include "TextureManager.hpp"

MovableObject::MovableObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
                             float scale, double rotation)
    : GameObject(id, x, y, w, h, color, scale, rotation),
      velocity(0, 0),
      facingDirection(FacingDirection::LEFT) {}

void MovableObject::draw() {
    SDL_RendererFlip flip = (facingDirection == FacingDirection::LEFT) ? SDL_FLIP_HORIZONTAL : SDL_FLIP_NONE;
    _TextureManager::Instance().draw(id, renderRect, rotation, flip);
}