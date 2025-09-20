#pragma once

#include "Vector2D.hpp"
#include <SDL.h>
#include <vector>

enum MouseButtons {
    LEFT = 0,
    MIDDLE = 1,
    RIGHT = 2
};

class InputHandler {
public:
    void init();
    void update();
    void clean();

    bool isKeyDown(SDL_Scancode key);

    bool getMouseButtonState(MouseButtons mouseButton);
    Vector2D &getMousePos();

    static InputHandler &Instance() {
        static InputHandler instance;
        return instance;
    }

private:
    InputHandler() {}
    ~InputHandler() {}
    InputHandler(const InputHandler &) = delete;
    InputHandler &operator=(const InputHandler &) = delete;

    const Uint8 *keystates;

    std::vector<bool> mouseButtonStates;
    Vector2D mousePos;

    void onKeyDown(SDL_Event &event);
    void onKeyUp(SDL_Event &event);

    void onMouseMove(SDL_Event &event);
    void onMouseButtonDown(SDL_Event &event);
    void onMouseButtonUp(SDL_Event &event);

    void reset();
};

using _InputHandler = InputHandler;