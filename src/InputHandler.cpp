#include "InputHandler.hpp"
#include "Game.hpp"
#include <iostream>

void InputHandler::init() {
    mouseButtonStates = {false, false, false};
    mousePos = {0, 0};
}

void InputHandler::update() {
    keystates = SDL_GetKeyboardState(nullptr);

    SDL_Event event;
    while (SDL_PollEvent(&event)) {
        switch (event.type) {
        case SDL_QUIT:
            _Game::Instance().quit();
            break;

        case SDL_KEYDOWN:
            onKeyDown(event);
            break;
        case SDL_KEYUP:
            onKeyUp(event);
            break;

        case SDL_MOUSEMOTION:
            onMouseMove(event);
            break;
        case SDL_MOUSEBUTTONDOWN:
            onMouseButtonDown(event);
            break;
        case SDL_MOUSEBUTTONUP:
            onMouseButtonUp(event);
            break;

        default:
            break;
        }
    }
}

void InputHandler::onKeyDown(SDL_Event &event) {
    // std::cout << "Key Pressed: " << SDL_GetKeyName(event.key.keysym.sym) << std::endl;
    _Game::Instance().getGameStateMachine().onKeyDown(event);
}

void InputHandler::onKeyUp(SDL_Event &event) {
    // std::cout << "Key Released: " << SDL_GetKeyName(event.key.keysym.sym) << std::endl;
    _Game::Instance().getGameStateMachine().onKeyUp(event);
}

bool InputHandler::isKeyDown(SDL_Scancode key) {
    if (keystates != 0) {
        if (keystates[key] == 1) {
            return true;
        } else {
            return false;
        }
    }
    return false;
}

void InputHandler::onMouseMove(SDL_Event &event) {
    // std::cout << "Mouse position = x: " << mousePos->x << ", y:" << mousePos->y << std::endl;
    mousePos.x = event.motion.x;
    mousePos.y = event.motion.y;
    _Game::Instance().getGameStateMachine().onMouseMove(event);
}

void InputHandler::onMouseButtonDown(SDL_Event &event) {
    if (event.button.button == SDL_BUTTON_LEFT) {
        // std::cout << "Left Mouse Button Pressed." << std::endl;
        mouseButtonStates[LEFT] = true;
    } else if (event.button.button == SDL_BUTTON_MIDDLE) {
        // std::cout << "Middle Mouse Button Pressed." << std::endl;
        mouseButtonStates[MIDDLE] = true;
    } else if (event.button.button == SDL_BUTTON_RIGHT) {
        // std::cout << "Right Mouse Button Pressed." << std::endl;
        mouseButtonStates[RIGHT] = true;
    }
    _Game::Instance().getGameStateMachine().onMouseButtonDown(event);
}

void InputHandler::onMouseButtonUp(SDL_Event &event) {
    if (event.button.button == SDL_BUTTON_LEFT) {
        // std::cout << "Left Mouse Button Released." << std::endl;
        mouseButtonStates[LEFT] = false;
    } else if (event.button.button == SDL_BUTTON_MIDDLE) {
        // std::cout << "Middle Mouse Button Released." << std::endl;
        mouseButtonStates[MIDDLE] = false;
    } else if (event.button.button == SDL_BUTTON_RIGHT) {
        // std::cout << "Right Mouse Button Released." << std::endl;
        mouseButtonStates[RIGHT] = false;
    }
    _Game::Instance().getGameStateMachine().onMouseButtonUp(event);
}

bool InputHandler::getMouseButtonState(MouseButtons mouseButton) {
    return mouseButtonStates[mouseButton];
}

Vector2D &InputHandler::getMousePos() {
    return mousePos;
}

void InputHandler::reset() {
    mouseButtonStates = {false, false, false};
}

void InputHandler::clean() {
}