#include "Platform.hpp"

Platform::Platform(const std::string &id, float x, float y, float w, float h, const SDL_Color &color, float scale, double rotation)
    : NonMovableObject(id, x, y, w, h, color, scale, rotation) {}