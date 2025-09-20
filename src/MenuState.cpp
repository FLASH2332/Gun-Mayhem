#include "MenuState.hpp"

bool MenuState::onEnter() {
    std::cout << "entering MenuState..." << std::endl;
    return true;
}

bool MenuState::onExit() {
    std::cout << "exiting MenuState..." << std::endl;
    return true;
}

void MenuState::update(float deltaTime) {
}

void MenuState::render() {
}

void MenuState::onKeyDown(SDL_Event &event) {
}

void MenuState::onKeyUp(SDL_Event &event) {
}

void MenuState::onMouseButtonDown(SDL_Event &event) {
}

void MenuState::onMouseButtonUp(SDL_Event &event) {
}

void MenuState::onMouseMove(SDL_Event &event) {
}
