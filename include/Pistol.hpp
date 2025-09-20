#pragma once

#include "RangedWeapon.hpp"

class Pistol : public RangedWeapon {
public:
    Pistol(const std::string &id, const std::string &playerId, float x, float y, float w, float h, const SDL_Color &color, float scale = 1, double rotation = 0);

    std::string getName() const override { return "Pistol"; }
};