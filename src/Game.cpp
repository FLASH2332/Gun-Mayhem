#include "Game.hpp"
#include "InputHandler.hpp"
#include "PlayState.hpp"
#include "utils.hpp"
#include <iostream>

bool Game::init(const std::string &title, int x, int y, int windowFlags) {
    screenSize = utils::loadScreenSizeFromJson("../assets/gameConfig.json");

    if (SDL_Init(SDL_INIT_EVERYTHING) == 0) {
        std::cout << "SDL initialized." << std::endl;
    } else {
        std::cout << "SDL initialization failed." << std::endl;
        return false;
    }

    if (TTF_Init() == 0) {
        std::cout << "TTF initialized." << std::endl;
        font = TTF_OpenFont("../assets/fonts/Roboto-Italic.ttf", 10);
        if (!font) {
            std::cout << "Font load error: " << TTF_GetError() << std::endl;
        }
    } else {
        std::cout << "TTF initialization failed: " << TTF_GetError() << std::endl;
        return false;
    }

    window = SDL_CreateWindow(title.c_str(), x, y, screenSize.width, screenSize.height, windowFlags);
    if (window != 0) {
        std::cout << "Window created." << std::endl;
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
    } else {
        std::cout << "Window creation failed." << std::endl;
        return false;
    }

    renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);
    if (renderer != nullptr) {
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
        SDL_RenderSetLogicalSize(renderer, screenSize.width, screenSize.height);
        std::cout << "Renderer created." << std::endl;
    } else {
        std::cout << "Renderer creation failed" << std::endl;
        return false;
    }

    _InputHandler::Instance().init();

    gameStateMachine = GameStateMachine();
    gameStateMachine.pushState(new PlayState());

    running = true;
    return true;
}

void Game::render() {
    SDL_SetRenderDrawColor(renderer, 50, 50, 50, 255);
    SDL_RenderClear(renderer);

    gameStateMachine.render();
    SDL_RenderPresent(renderer);
}

void Game::update(float deltaTime) {
    // TODO: check this deltaTime limit
    if (deltaTime > 0.1f)
        deltaTime = 0.1f;
    gameStateMachine.update(deltaTime);
}

void Game::handleEvents() {
    _InputHandler::Instance().update();
}

void Game::clean() {
    SDL_DestroyWindow(window);
    SDL_DestroyRenderer(renderer);
    TTF_Quit();
    SDL_Quit();
}

void Game::quit() {
    running = false;
    while (gameStateMachine.getGameStates().size() > 0) {
        gameStateMachine.popState();
    }
    clean();
}