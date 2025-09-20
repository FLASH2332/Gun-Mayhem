#include "GameObject.hpp"

class NonMovableObject : public GameObject {
public:
    NonMovableObject(const std::string &id, float x, float y, float w, float h, const SDL_Color &color,
                     float scale = 1, double rotation = 0);

private:
};