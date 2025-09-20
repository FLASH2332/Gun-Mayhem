#include "Timer.hpp"
#include <iostream>

Timer::Timer(int targetFPS) : targetFPS(targetFPS) {
    frameDelay = 1000 / targetFPS;
    lastFrameTime = SDL_GetTicks();
}

void Timer::startFrame() {
    frameStart = SDL_GetTicks();
    deltaTime = (frameStart - lastFrameTime) / 1000.0f;
    lastFrameTime = frameStart;
}

void Timer::endFrame() const {
    int frameTime = SDL_GetTicks() - frameStart;
    if (frameTime < frameDelay) {
        SDL_Delay(frameDelay - frameTime);
    }
    else {
        // std::cout << "Frame took too long: " << frameTime << " ms, expected: " << frameDelay << " ms" << std::endl;
    }
}

float Timer::getFPS() const {
    return 1.0f / deltaTime;
}

float Timer::getDeltaTime() const {
    return deltaTime;
}