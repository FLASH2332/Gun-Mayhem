#include "NonMovableObject.hpp"

NonMovableObject::NonMovableObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
                                   float scale, double rotation)
    : GameObject(id, x, y, w, h, color, scale, rotation) {}
