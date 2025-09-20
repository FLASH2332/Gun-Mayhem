#include "Vector2D.hpp"
#include <math.h>

float Vector2D::length() const {
    return sqrt(x * x + y * y);
}

// void Vector2D::setX(float X) {
//     x = X;
// }

// void Vector2D::setY(float Y) {
//     y = Y;
// }

// void Vector2D::setXY(float X, float Y) {
//     x = X;
//     y = Y;
// };
void Vector2D::normalise() {
    float l = length();
    if (l > 0) {
        (*this) *= 1 / l;
    }
}

Vector2D Vector2D::operator+(const Vector2D &v2) const {
    return Vector2D(x + v2.x, y + v2.y);
}

Vector2D &Vector2D::operator+=(const Vector2D &v2) {
    x += v2.x;
    y += v2.y;

    return *this;
}

Vector2D Vector2D::operator-(const Vector2D &v2) const {
    return Vector2D(x - v2.x, y - v2.y);
}

Vector2D &Vector2D::operator-=(const Vector2D &v2) {
    x -= v2.x;
    y -= v2.y;

    return *this;
}

Vector2D Vector2D::operator*(float scalar) {
    return Vector2D(x * scalar, y * scalar);
}

Vector2D &Vector2D::operator*=(float scalar) {
    x *= scalar;
    y *= scalar;

    return *this;
}

Vector2D Vector2D::operator/(float scalar) {
    return Vector2D(x / scalar, y / scalar);
}

Vector2D &Vector2D::operator/=(float scalar) {
    x /= scalar;
    y /= scalar;

    return *this;
}