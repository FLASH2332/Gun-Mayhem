#pragma once

#include "GameStateMachine.hpp"
#include <SDL.h>
#include <SDL_ttf.h>
#include <string>
#include "utils.hpp"

class Game {
public:
    bool init(const std::string &title, int x, int y, int windowFlags);

    void update(float deltaTime);
    void handleEvents();
    void render();
    void clean();
    void quit();

    TTF_Font *getFont() const { return font; }
    SDL_Window *getWindow() const { return window; }
    SDL_Renderer *getRenderer() const { return renderer; }
    bool isRunning() { return running; }

    GameStateMachine &getGameStateMachine() { return gameStateMachine; }

    static Game &Instance() {
        static Game instance;
        return instance;
    }

    utils::ScreenSize getScreenSize() const { return screenSize; }

private:
    Game() {}
    ~Game() {}
    Game(const Game &) = delete;
    Game &operator=(const Game &) = delete;

    TTF_Font *font;
    SDL_Window *window;
    SDL_Renderer *renderer;
    GameStateMachine gameStateMachine;

    bool running;

    utils::ScreenSize screenSize;
};

using _Game = Game;