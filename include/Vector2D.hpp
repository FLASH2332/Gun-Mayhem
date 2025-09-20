#pragma once

class Vector2D {
public:
    Vector2D() : x(0), y(0) {};
    Vector2D(float X, float Y) : x(X), y(Y) {}
    ~Vector2D() {}

    // float x const { return x; }
    // float y const { return y; }
    // void setX(float X);
    // void setY(float Y);
    // void setXY(float X,float Y);
    float length() const;
    void normalise();

    Vector2D operator+(const Vector2D &v2) const;
    Vector2D &operator+=(const Vector2D &v2);
    Vector2D operator-(const Vector2D &v2) const;
    Vector2D &operator-=(const Vector2D &v2);
    Vector2D operator*(float scalar);
    Vector2D &operator*=(float scalar);
    Vector2D operator/(float scalar);
    Vector2D &operator/=(float scalar);

    float x, y;

private:
};
