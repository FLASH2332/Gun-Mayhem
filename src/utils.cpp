#include "utils.hpp"
#include "Pistol.hpp"
#include "json.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
using json = nlohmann::json;

utils::MapData utils::loadRandomMapFromJson(const std::string &filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cout << "Failed to open map file: " << filename << std::endl;
        return {};
    }

    json data;
    file >> data;

    const auto &mapData = data["maps"];

    std::vector<std::string> mapNames;
    for (auto &entry : mapData.items()) {
        mapNames.push_back(entry.key());
    }

    if (mapNames.empty())
        return {};

    srand(static_cast<unsigned>(time(nullptr)));
    std::string selectedMap = mapNames[rand() % mapNames.size()];
    const auto &map = mapData[selectedMap];

    std::vector<std::unique_ptr<Platform>> platforms;
    for (const auto &p : map["platforms"]) {
        SDL_Color color = {
            p["color"]["r"],
            p["color"]["g"],
            p["color"]["b"],
            p["color"]["a"]};

        std::unique_ptr<Platform> platform = std::make_unique<Platform>(p["id"], p["x"], p["y"], p["w"], p["h"], color);

        platforms.push_back(std::move(platform));
    }

    std::vector<SDL_Point> spawnPoints;
    for (const auto &s : map["spawnPoints"]) {
        spawnPoints.push_back({s["x"], s["y"]});
    }

    return {std::move(platforms), spawnPoints, selectedMap};
}

utils::PlayerData utils::loadPlayersFromJson(const std::string &filename, const std::vector<SDL_Point> &spawnPoints) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cout << "Failed to open player config file: " << filename << std::endl;
        return {};
    }

    json data;
    file >> data;

    const auto &playersData = data["players"];
    std::vector<std::unique_ptr<Player>> players;

    int i = 0;
    for (auto &[key, value] : playersData.items()) {

        std::string id = value["id"];
        int w = value["w"];
        int h = value["h"];
        SDL_Color color = {
            value["color"]["r"],
            value["color"]["g"],
            value["color"]["b"],
            value["color"]["a"]};

        int x = spawnPoints[i].x;
        int y = spawnPoints[i].y;

        std::unique_ptr<Player> player = std::make_unique<Player>(id, x, y, w, h, color);
        players.push_back(std::move(player));
        i++;
    }

    return {std::move(players)};
}

utils::ScreenSize utils::loadScreenSizeFromJson(const std::string &filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cout << "Failed to open screen size config file: " << filename << std::endl;
    }

    json data;
    file >> data;

    return {data["screen"]["width"], data["screen"]["height"]};
}

std::unordered_map<std::string, utils::PlayerControls> utils::loadPlayerControls(const std::string &filePath) {
    static std::unordered_map<std::string, SDL_Scancode> keyNameToScanCode = {
        {"A", SDL_SCANCODE_A},
        {"B", SDL_SCANCODE_B},
        {"D", SDL_SCANCODE_D},
        {"S", SDL_SCANCODE_S},
        {"W", SDL_SCANCODE_W},
        {"T", SDL_SCANCODE_T},
        {"Y", SDL_SCANCODE_Y},
        {"Z", SDL_SCANCODE_Z},
        {"X", SDL_SCANCODE_X},
        {"1", SDL_SCANCODE_1},
        {"Q", SDL_SCANCODE_Q},
        {"UP", SDL_SCANCODE_UP},
        {"DOWN", SDL_SCANCODE_DOWN},
        {"LEFT", SDL_SCANCODE_LEFT},
        {"RIGHT", SDL_SCANCODE_RIGHT},
        {"LESS", SDL_SCANCODE_COMMA},
        {"GREATER", SDL_SCANCODE_PERIOD}};

    std::ifstream file(filePath);
    json data;
    file >> data;

    std::unordered_map<std::string, utils::PlayerControls> controlsMap;

    for (auto &[playerKey, playerInfo] : data["players"].items()) {
        auto &ctrl = playerInfo["controls"];
        utils::PlayerControls pc;
        pc.up = keyNameToScanCode[ctrl["up"]];
        pc.down = keyNameToScanCode[ctrl["down"]];
        pc.left = keyNameToScanCode[ctrl["left"]];
        pc.right = keyNameToScanCode[ctrl["right"]];
        pc.primaryShoot = keyNameToScanCode[ctrl["primaryShoot"]];
        pc.secondaryShoot = keyNameToScanCode[ctrl["secondaryShoot"]];
        controlsMap[playerInfo["id"]] = pc;
    }

    return controlsMap;
}

std::unique_ptr<Weapon> utils::createWeapon(const std::string &type, const std::string &playerId, float x, float y,
                                            float scale, double rotation) {
    std::ifstream file("../assets/gameConfig.json");
    if (!file.is_open()) {
        std::cout << "Failed to open map file: " << "../assets/gameConfig.json" << std::endl;
        return {};
    }

    json data;
    file >> data;

    const auto &weaponInfo = data["weapons"][type];
    SDL_Color color = {
        weaponInfo["color"]["r"],
        weaponInfo["color"]["g"],
        weaponInfo["color"]["b"],
        weaponInfo["color"]["a"]};

    std::unique_ptr<Weapon> weapon;

    if (type == "pistol") {
        weapon = std::make_unique<Pistol>(std::string(weaponInfo["id"]) + "_" + playerId, playerId, x, y, weaponInfo["w"],
                                          weaponInfo["h"], color);
    }
    return std::move(weapon);
}
