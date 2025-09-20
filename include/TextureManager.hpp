#pragma once

#include <SDL.h>
#include <map>
#include <string>

class TextureManager {
public:
    bool createTextureFromRect(const std::string &id, const SDL_FRect &rect, const SDL_Color &color);
    void draw(const std::string &id, SDL_FRect &rect, double angle , SDL_RendererFlip flip = SDL_FLIP_NONE, const SDL_FPoint *center = nullptr);
    void removeFromTextureMap(const std::string &id);

    static TextureManager &Instance() {
        static TextureManager instance;
        return instance;
    }

private:
    TextureManager() {}
    ~TextureManager() {}
    TextureManager(const TextureManager &) = delete;
    TextureManager &operator=(const TextureManager &) = delete;

    std::map<std::string, SDL_Texture *> textureMap;
};

typedef TextureManager _TextureManager;
// typedef std::map<std::string, SDL_Texture *>::iterator textureMapIterator;