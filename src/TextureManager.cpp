#include "TextureManager.hpp"
#include "Game.hpp"
#include <iostream>

bool TextureManager::createTextureFromRect(const std::string &id, const SDL_FRect &rect, const SDL_Color &color) {
    SDL_Renderer *renderer = _Game::Instance().getRenderer();

    SDL_Surface *surface = SDL_CreateRGBSurfaceWithFormat(0, int(rect.w), int(rect.h), 32, SDL_PIXELFORMAT_RGBA32);
    SDL_FillRect(surface, NULL, SDL_MapRGBA(surface->format, color.r, color.g, color.b, color.a));
    SDL_Texture *texture = SDL_CreateTextureFromSurface(renderer, surface);
    SDL_FreeSurface(surface);

    textureMap[id] = texture;
    return true;
}

void TextureManager::draw(const std::string &id, SDL_FRect &rect, double angle, SDL_RendererFlip flip, const SDL_FPoint *center) {
    auto it = textureMap.find(id);
    if (it == textureMap.end()) {
        std::cout << "Texture with ID '" << id << "' not found in texture map." << std::endl;
        return;
    }
    SDL_RenderCopyExF(_Game::Instance().getRenderer(), textureMap[id], NULL, &rect, angle, center, flip);
}

void TextureManager::removeFromTextureMap(const std::string &id) {
    if (textureMap.find(id) != textureMap.end()) {
        SDL_DestroyTexture(textureMap[id]);
        textureMap.erase(id);
    }
}