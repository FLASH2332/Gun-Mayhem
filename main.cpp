#define SDL_MAIN_HANDLED

#include "Game.hpp"
#include "Timer.hpp"
#include <SDL.h>
#include <iostream>

int main(int argc, char *argv[]) {
    if (_Game::Instance().init("Gun Mayhem", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, SDL_WINDOW_RESIZABLE)) {
        std::cout << "Game init successful." << std::endl;

        const int FPS = 60;
        Timer timer = Timer(FPS);

        while (_Game::Instance().isRunning()) {
            timer.startFrame();

            _Game::Instance().handleEvents();
            _Game::Instance().update(timer.getDeltaTime());
            _Game::Instance().render();

            timer.endFrame();
        }
    } else {
        std::cout << "Game init failed: " << SDL_GetError() << std::endl;
        return -1;
    }

    return 0;
}