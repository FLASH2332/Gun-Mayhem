#pragma once

#include "Pistol.hpp"
#include "Platform.hpp"
#include "Player.hpp"
#include "Weapon.hpp"
#include <SDL.h>
#include <memory>
#include <string>
#include <unordered_map>
#include <vector>

namespace utils {
    struct MapData {
        std::vector<std::unique_ptr<Platform>> platforms;
        std::vector<SDL_Point> spawnPoints;
        std::string mapName;
    };
    MapData loadRandomMapFromJson(const std::string &filename);

    struct PlayerData {
        std::vector<std::unique_ptr<Player>> players;
    };
    PlayerData loadPlayersFromJson(const std::string &filename, const std::vector<SDL_Point> &spawnPoints);

    struct ScreenSize {
        int width;
        int height;
    };
    ScreenSize loadScreenSizeFromJson(const std::string &filename);

    struct PlayerControls {
        SDL_Scancode up;
        SDL_Scancode down;
        SDL_Scancode left;
        SDL_Scancode right;
        SDL_Scancode primaryShoot;
        SDL_Scancode secondaryShoot;
    };
    std::unordered_map<std::string, utils::PlayerControls> loadPlayerControls(const std::string &filePath);

    std::unique_ptr<Weapon> createWeapon(const std::string &type, const std::string &playerId, float x, float y,
                                         float scale = 1, double rotation = 0);
}