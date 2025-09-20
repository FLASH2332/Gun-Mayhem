#pragma once

#include "SDL.h"

class Timer {
public:
    Timer(int targetFPS);
    ~Timer() {}

    void startFrame();
    void endFrame() const;
    float getDeltaTime() const;
    float getFPS() const;

private:
    int targetFPS;
    int frameDelay;
    int frameStart;
    float deltaTime;
    int lastFrameTime;
};